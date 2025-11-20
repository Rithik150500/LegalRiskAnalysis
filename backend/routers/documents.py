# routers/documents.py - Document management endpoints
import os
import uuid
import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from database import get_db
from models import (
    DocumentModel, DocumentResponse, DocumentDetail
)

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    summary: str = Form(default=""),
    db: Session = Depends(get_db)
):
    """Upload a document for analysis"""

    # Generate unique document ID
    doc_id = f"DOC{str(uuid.uuid4())[:8].upper()}"

    # Determine file type
    file_extension = os.path.splitext(file.filename)[1].lower()
    file_type = file_extension.replace(".", "").upper()

    # Save file
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}{file_extension}")

    content = await file.read()
    file_size = len(content)

    with open(file_path, "wb") as f:
        f.write(content)

    # Process document to extract page info (simplified)
    page_count = 1
    pages_data = []

    if file_extension == ".pdf":
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            page_count = len(reader.pages)

            for i, page in enumerate(reader.pages):
                text = page.extract_text()[:500] if page.extract_text() else ""
                pages_data.append({
                    "page_num": i + 1,
                    "summdesc": f"Page {i + 1}: {text[:200]}..." if text else f"Page {i + 1}",
                    "has_image": False
                })
        except Exception as e:
            print(f"Error processing PDF: {e}")
            pages_data = [{"page_num": 1, "summdesc": "Document page", "has_image": False}]
    else:
        pages_data = [{"page_num": 1, "summdesc": "Document content", "has_image": False}]

    # Auto-generate summary if not provided
    if not summary:
        summary = f"{file.filename} - {file_type} document with {page_count} pages"

    # Create database record
    db_document = DocumentModel(
        doc_id=doc_id,
        filename=f"{doc_id}{file_extension}",
        original_filename=file.filename,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        summary=summary,
        page_count=page_count,
        pages_data=pages_data
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return db_document

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all uploaded documents"""
    documents = db.query(DocumentModel).offset(skip).limit(limit).all()
    return documents

@router.get("/{doc_id}", response_model=DocumentDetail)
async def get_document(doc_id: str, db: Session = Depends(get_db)):
    """Get document details by ID"""
    document = db.query(DocumentModel).filter(DocumentModel.doc_id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
    return document

@router.delete("/{doc_id}")
async def delete_document(doc_id: str, db: Session = Depends(get_db)):
    """Delete a document"""
    document = db.query(DocumentModel).filter(DocumentModel.doc_id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

    # Delete file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    db.delete(document)
    db.commit()

    return {"message": f"Document {doc_id} deleted successfully"}

@router.put("/{doc_id}/summary")
async def update_document_summary(
    doc_id: str,
    summary: str = Form(...),
    db: Session = Depends(get_db)
):
    """Update document summary"""
    document = db.query(DocumentModel).filter(DocumentModel.doc_id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

    document.summary = summary
    db.commit()
    db.refresh(document)

    return document

@router.get("/{doc_id}/pages")
async def get_document_pages(
    doc_id: str,
    page_nums: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get document page information"""
    document = db.query(DocumentModel).filter(DocumentModel.doc_id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

    pages = document.pages_data or []

    if page_nums:
        try:
            requested_pages = [int(p) for p in page_nums.split(",")]
            pages = [p for p in pages if p.get("page_num") in requested_pages]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid page numbers format")

    return {
        "doc_id": doc_id,
        "total_pages": document.page_count,
        "pages": pages
    }
