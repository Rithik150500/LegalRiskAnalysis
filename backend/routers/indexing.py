# routers/indexing.py - Data Room Indexing endpoints
import os
import uuid
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models import DocumentModel
from services.indexing_pipeline import DataRoomIndexingPipeline

router = APIRouter()

# In-memory storage for indexing job status
indexing_jobs: Dict[str, Dict[str, Any]] = {}


# Pydantic models for indexing
class IndexingJobCreate(BaseModel):
    document_ids: List[str]
    name: Optional[str] = None


class IndexingJobStatus(BaseModel):
    job_id: str
    name: str
    status: str  # pending, running, completed, failed
    progress: int
    current_step: str
    total_documents: int
    processed_documents: int
    created_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


class DocumentIndexResult(BaseModel):
    doc_id: str
    filename: str
    page_count: int
    summary: str
    pages: List[Dict[str, Any]]


UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


async def update_job_progress(job_id: str, doc_id: str, progress: int, step: str):
    """Update indexing job progress"""
    if job_id in indexing_jobs:
        if doc_id == 'index':
            indexing_jobs[job_id]['progress'] = progress
        indexing_jobs[job_id]['current_step'] = step


async def run_indexing_job(job_id: str, documents: List[Dict[str, Any]], db: Session):
    """Background task to run the indexing pipeline"""
    try:
        indexing_jobs[job_id]['status'] = 'running'
        indexing_jobs[job_id]['current_step'] = 'Initializing pipeline'

        pipeline = DataRoomIndexingPipeline()

        # Create progress callback
        async def progress_callback(doc_id: str, progress: int, step: str):
            await update_job_progress(job_id, doc_id, progress, step)

        # Run the indexing pipeline
        result = await pipeline.build_data_room_index(
            documents,
            progress_callback=progress_callback
        )

        # Update documents in database with new summaries and page data
        for indexed_doc in result['documents']:
            doc = db.query(DocumentModel).filter(
                DocumentModel.doc_id == indexed_doc['doc_id']
            ).first()

            if doc:
                doc.summary = indexed_doc['summdesc']
                doc.page_count = indexed_doc['page_count']
                # Store page data (remove base64 images to save space)
                pages_data = []
                for page in indexed_doc['pages_data']:
                    pages_data.append({
                        'page_num': page['page_num'],
                        'summdesc': page['summdesc'],
                        'image_path': page.get('image_path', ''),
                        'has_image': page.get('has_image', True)
                    })
                doc.pages_data = pages_data

        db.commit()

        # Update job status
        indexing_jobs[job_id]['status'] = 'completed'
        indexing_jobs[job_id]['progress'] = 100
        indexing_jobs[job_id]['current_step'] = 'Complete'
        indexing_jobs[job_id]['completed_at'] = datetime.utcnow().isoformat()
        indexing_jobs[job_id]['processed_documents'] = len(result['documents'])
        indexing_jobs[job_id]['result'] = {
            'index_id': result['index_id'],
            'total_documents': result['total_documents'],
            'total_pages': result['total_pages'],
            'documents': [
                {
                    'doc_id': doc['doc_id'],
                    'filename': doc['original_filename'],
                    'page_count': doc['page_count'],
                    'summary': doc['summdesc']
                }
                for doc in result['documents']
            ]
        }

    except Exception as e:
        indexing_jobs[job_id]['status'] = 'failed'
        indexing_jobs[job_id]['error_message'] = str(e)
        indexing_jobs[job_id]['current_step'] = 'Failed'
        raise


@router.post("/start", response_model=IndexingJobStatus)
async def start_indexing(
    request: IndexingJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start indexing documents to build data room index"""

    # Validate document IDs
    documents = []
    for doc_id in request.document_ids:
        doc = db.query(DocumentModel).filter(DocumentModel.doc_id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

        documents.append({
            'doc_id': doc.doc_id,
            'file_path': doc.file_path,
            'original_filename': doc.original_filename
        })

    # Create indexing job
    job_id = f"IDX{str(uuid.uuid4())[:8].upper()}"
    job_name = request.name or f"Indexing Job {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"

    indexing_jobs[job_id] = {
        'job_id': job_id,
        'name': job_name,
        'status': 'pending',
        'progress': 0,
        'current_step': 'Queued',
        'total_documents': len(documents),
        'processed_documents': 0,
        'created_at': datetime.utcnow().isoformat(),
        'completed_at': None,
        'error_message': None,
        'result': None
    }

    # Start background task
    background_tasks.add_task(run_indexing_job, job_id, documents, db)

    return IndexingJobStatus(**indexing_jobs[job_id])


@router.get("/jobs", response_model=List[IndexingJobStatus])
async def list_indexing_jobs():
    """List all indexing jobs"""
    return [IndexingJobStatus(**job) for job in indexing_jobs.values()]


@router.get("/jobs/{job_id}", response_model=IndexingJobStatus)
async def get_indexing_job(job_id: str):
    """Get indexing job status"""
    if job_id not in indexing_jobs:
        raise HTTPException(status_code=404, detail=f"Indexing job {job_id} not found")

    return IndexingJobStatus(**indexing_jobs[job_id])


@router.post("/upload-and-index", response_model=IndexingJobStatus)
async def upload_and_index(
    files: List[UploadFile] = File(...),
    name: str = Form(default=""),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Upload multiple files and immediately start indexing them"""

    documents = []

    # First, upload all files
    for file in files:
        doc_id = f"DOC{str(uuid.uuid4())[:8].upper()}"
        file_extension = os.path.splitext(file.filename)[1].lower()
        file_type = file_extension.replace(".", "").upper()

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, f"{doc_id}{file_extension}")

        content = await file.read()
        file_size = len(content)

        with open(file_path, "wb") as f:
            f.write(content)

        # Create database record
        db_document = DocumentModel(
            doc_id=doc_id,
            filename=f"{doc_id}{file_extension}",
            original_filename=file.filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            summary="Pending indexing...",
            page_count=0,
            pages_data=[]
        )

        db.add(db_document)
        documents.append({
            'doc_id': doc_id,
            'file_path': file_path,
            'original_filename': file.filename
        })

    db.commit()

    # Create indexing job
    job_id = f"IDX{str(uuid.uuid4())[:8].upper()}"
    job_name = name or f"Upload & Index {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"

    indexing_jobs[job_id] = {
        'job_id': job_id,
        'name': job_name,
        'status': 'pending',
        'progress': 0,
        'current_step': 'Queued',
        'total_documents': len(documents),
        'processed_documents': 0,
        'created_at': datetime.utcnow().isoformat(),
        'completed_at': None,
        'error_message': None,
        'result': None
    }

    # Start background task
    background_tasks.add_task(run_indexing_job, job_id, documents, db)

    return IndexingJobStatus(**indexing_jobs[job_id])


@router.get("/index/{doc_id}")
async def get_document_index(doc_id: str, db: Session = Depends(get_db)):
    """Get the indexed data for a specific document"""

    doc = db.query(DocumentModel).filter(DocumentModel.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

    return {
        'doc_id': doc.doc_id,
        'filename': doc.original_filename,
        'summary': doc.summary,
        'page_count': doc.page_count,
        'pages': doc.pages_data
    }


@router.get("/data-room")
async def get_data_room_index(db: Session = Depends(get_db)):
    """Get the complete data room index with all indexed documents"""

    documents = db.query(DocumentModel).all()

    indexed_docs = []
    for doc in documents:
        if doc.pages_data and len(doc.pages_data) > 0:
            indexed_docs.append({
                'doc_id': doc.doc_id,
                'filename': doc.original_filename,
                'file_type': doc.file_type,
                'summary': doc.summary,
                'page_count': doc.page_count,
                'pages': doc.pages_data,
                'uploaded_at': doc.uploaded_at.isoformat() if doc.uploaded_at else None
            })

    return {
        'total_documents': len(indexed_docs),
        'total_pages': sum(doc['page_count'] for doc in indexed_docs),
        'documents': indexed_docs
    }


@router.delete("/jobs/{job_id}")
async def delete_indexing_job(job_id: str):
    """Delete an indexing job record"""
    if job_id not in indexing_jobs:
        raise HTTPException(status_code=404, detail=f"Indexing job {job_id} not found")

    del indexing_jobs[job_id]
    return {"message": f"Indexing job {job_id} deleted"}
