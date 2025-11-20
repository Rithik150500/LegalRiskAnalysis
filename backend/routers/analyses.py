# routers/analyses.py - Analysis management endpoints
import os
import sys
import uuid
import json
import asyncio
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import get_db
from models import (
    AnalysisModel, AnalysisStatus, DocumentModel, RiskModel,
    AnalysisCreate, AnalysisResponse, AnalysisDetail, AnalysisDocuments,
    RiskCategory, RiskSeverity, RiskLikelihood
)

router = APIRouter()

# Store for analysis progress updates
analysis_progress = {}

def run_analysis_task(analysis_id: str, document_ids: List[str], db_url: str):
    """Background task to run the legal risk analysis"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Create new database session for background task
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Get analysis record
        analysis = db.query(AnalysisModel).filter(AnalysisModel.analysis_id == analysis_id).first()
        if not analysis:
            return

        # Update status to running
        analysis.status = AnalysisStatus.RUNNING
        analysis.started_at = datetime.utcnow()
        analysis.current_step = "Initializing analysis..."
        analysis.progress = 5
        db.commit()

        # Get documents
        documents = db.query(DocumentModel).filter(DocumentModel.doc_id.in_(document_ids)).all()

        # Simulate analysis phases (in production, this would call the actual agent)
        phases = [
            ("Loading documents...", 10),
            ("Analyzing contractual risks...", 25),
            ("Analyzing regulatory compliance...", 40),
            ("Analyzing litigation exposure...", 55),
            ("Analyzing IP concerns...", 70),
            ("Analyzing operational risks...", 85),
            ("Generating report...", 95),
        ]

        # Generate mock risk data for demonstration
        risks_data = []
        risk_counter = 1

        for doc in documents:
            # Generate sample risks for each document
            sample_risks = [
                {
                    "risk_id": f"RISK_{risk_counter:03d}",
                    "category": RiskCategory.CONTRACTUAL,
                    "title": f"Liability limitation in {doc.original_filename}",
                    "description": "The liability cap may be insufficient to cover potential damages in case of service failure.",
                    "severity": RiskSeverity.HIGH,
                    "likelihood": RiskLikelihood.POSSIBLE,
                    "evidence": [{"doc_id": doc.doc_id, "page_num": 1, "citation": "Liability shall not exceed fees paid in prior 12 months"}],
                    "legal_basis": "Contract Law - Limitation of Liability Clauses",
                    "recommended_mitigation": "Negotiate higher liability caps or carve-outs for gross negligence"
                },
                {
                    "risk_id": f"RISK_{risk_counter + 1:03d}",
                    "category": RiskCategory.REGULATORY,
                    "title": f"Data protection compliance in {doc.original_filename}",
                    "description": "Potential gaps in GDPR compliance for cross-border data transfers.",
                    "severity": RiskSeverity.MEDIUM,
                    "likelihood": RiskLikelihood.LIKELY,
                    "evidence": [{"doc_id": doc.doc_id, "page_num": 2, "citation": "Data may be processed in any jurisdiction"}],
                    "legal_basis": "GDPR Article 44-49",
                    "recommended_mitigation": "Implement Standard Contractual Clauses for international transfers"
                },
                {
                    "risk_id": f"RISK_{risk_counter + 2:03d}",
                    "category": RiskCategory.OPERATIONAL,
                    "title": f"Service continuity risk in {doc.original_filename}",
                    "description": "No clear disaster recovery or business continuity provisions.",
                    "severity": RiskSeverity.MEDIUM,
                    "likelihood": RiskLikelihood.POSSIBLE,
                    "evidence": [{"doc_id": doc.doc_id, "page_num": 1, "citation": "Service availability target: 99.9%"}],
                    "legal_basis": "Industry best practices for service continuity",
                    "recommended_mitigation": "Request DR/BCP documentation and add SLA penalties"
                }
            ]

            risk_counter += 3
            risks_data.extend(sample_risks)

        # Simulate progress through phases
        import time
        for step, progress in phases:
            analysis.current_step = step
            analysis.progress = progress
            db.commit()
            time.sleep(0.5)  # Simulate work

        # Save risks to database
        for risk_data in risks_data:
            db_risk = RiskModel(
                risk_id=risk_data["risk_id"],
                analysis_id=analysis.id,
                category=risk_data["category"],
                title=risk_data["title"],
                description=risk_data["description"],
                severity=risk_data["severity"],
                likelihood=risk_data["likelihood"],
                evidence=risk_data["evidence"],
                legal_basis=risk_data["legal_basis"],
                recommended_mitigation=risk_data["recommended_mitigation"]
            )
            db.add(db_risk)

        # Store result data
        result_data = {
            "analysis_summary": f"Comprehensive legal risk analysis of {len(documents)} documents",
            "documents_analyzed": document_ids,
            "risks_identified": risks_data,
            "total_risks": len(risks_data),
            "by_severity": {
                "Critical": len([r for r in risks_data if r["severity"] == RiskSeverity.CRITICAL]),
                "High": len([r for r in risks_data if r["severity"] == RiskSeverity.HIGH]),
                "Medium": len([r for r in risks_data if r["severity"] == RiskSeverity.MEDIUM]),
                "Low": len([r for r in risks_data if r["severity"] == RiskSeverity.LOW]),
            }
        }

        # Update analysis as completed
        analysis.status = AnalysisStatus.COMPLETED
        analysis.completed_at = datetime.utcnow()
        analysis.progress = 100
        analysis.current_step = "Analysis complete"
        analysis.result_data = result_data
        analysis.report_path = f"/outputs/{analysis_id}_report.docx"
        analysis.dashboard_path = f"/outputs/{analysis_id}_dashboard.html"
        db.commit()

    except Exception as e:
        # Handle errors
        analysis = db.query(AnalysisModel).filter(AnalysisModel.analysis_id == analysis_id).first()
        if analysis:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            db.commit()
    finally:
        db.close()

@router.post("/", response_model=AnalysisResponse)
async def create_analysis(
    analysis_data: AnalysisCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create and start a new analysis"""

    # Validate documents exist
    documents = db.query(DocumentModel).filter(
        DocumentModel.doc_id.in_(analysis_data.document_ids)
    ).all()

    if len(documents) != len(analysis_data.document_ids):
        found_ids = {d.doc_id for d in documents}
        missing = set(analysis_data.document_ids) - found_ids
        raise HTTPException(
            status_code=404,
            detail=f"Documents not found: {', '.join(missing)}"
        )

    # Create analysis record
    analysis_id = f"ANA{str(uuid.uuid4())[:8].upper()}"

    db_analysis = AnalysisModel(
        analysis_id=analysis_id,
        name=analysis_data.name,
        description=analysis_data.description,
        status=AnalysisStatus.PENDING
    )

    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)

    # Link documents to analysis
    for doc in documents:
        assoc = AnalysisDocuments(
            analysis_id=db_analysis.id,
            document_id=doc.id
        )
        db.add(assoc)
    db.commit()

    # Get database URL for background task
    from database import DATABASE_URL

    # Start analysis in background
    background_tasks.add_task(
        run_analysis_task,
        analysis_id,
        analysis_data.document_ids,
        DATABASE_URL
    )

    # Return response with document count
    response = AnalysisResponse(
        id=db_analysis.id,
        analysis_id=db_analysis.analysis_id,
        name=db_analysis.name,
        description=db_analysis.description,
        status=db_analysis.status,
        progress=db_analysis.progress,
        current_step=db_analysis.current_step,
        created_at=db_analysis.created_at,
        started_at=db_analysis.started_at,
        completed_at=db_analysis.completed_at,
        error_message=db_analysis.error_message,
        document_count=len(documents),
        risk_count=0
    )

    return response

@router.get("/", response_model=List[AnalysisResponse])
async def list_analyses(
    skip: int = 0,
    limit: int = 100,
    status: Optional[AnalysisStatus] = None,
    db: Session = Depends(get_db)
):
    """List all analyses"""
    query = db.query(AnalysisModel)

    if status:
        query = query.filter(AnalysisModel.status == status)

    analyses = query.order_by(AnalysisModel.created_at.desc()).offset(skip).limit(limit).all()

    # Build response with counts
    results = []
    for analysis in analyses:
        doc_count = db.query(AnalysisDocuments).filter(
            AnalysisDocuments.analysis_id == analysis.id
        ).count()
        risk_count = db.query(RiskModel).filter(
            RiskModel.analysis_id == analysis.id
        ).count()

        results.append(AnalysisResponse(
            id=analysis.id,
            analysis_id=analysis.analysis_id,
            name=analysis.name,
            description=analysis.description,
            status=analysis.status,
            progress=analysis.progress,
            current_step=analysis.current_step,
            created_at=analysis.created_at,
            started_at=analysis.started_at,
            completed_at=analysis.completed_at,
            error_message=analysis.error_message,
            document_count=doc_count,
            risk_count=risk_count
        ))

    return results

@router.get("/{analysis_id}", response_model=AnalysisDetail)
async def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """Get analysis details by ID"""
    analysis = db.query(AnalysisModel).filter(
        AnalysisModel.analysis_id == analysis_id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")

    # Get associated documents
    doc_assocs = db.query(AnalysisDocuments).filter(
        AnalysisDocuments.analysis_id == analysis.id
    ).all()
    doc_ids = [assoc.document_id for assoc in doc_assocs]
    documents = db.query(DocumentModel).filter(DocumentModel.id.in_(doc_ids)).all()

    # Get risks
    risks = db.query(RiskModel).filter(RiskModel.analysis_id == analysis.id).all()

    return AnalysisDetail(
        id=analysis.id,
        analysis_id=analysis.analysis_id,
        name=analysis.name,
        description=analysis.description,
        status=analysis.status,
        progress=analysis.progress,
        current_step=analysis.current_step,
        created_at=analysis.created_at,
        started_at=analysis.started_at,
        completed_at=analysis.completed_at,
        error_message=analysis.error_message,
        result_data=analysis.result_data,
        report_path=analysis.report_path,
        dashboard_path=analysis.dashboard_path,
        documents=documents,
        risks=risks,
        document_count=len(documents),
        risk_count=len(risks)
    )

@router.get("/{analysis_id}/status")
async def get_analysis_status(analysis_id: str, db: Session = Depends(get_db)):
    """Get analysis status and progress"""
    analysis = db.query(AnalysisModel).filter(
        AnalysisModel.analysis_id == analysis_id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")

    return {
        "analysis_id": analysis.analysis_id,
        "status": analysis.status,
        "progress": analysis.progress,
        "current_step": analysis.current_step,
        "error_message": analysis.error_message
    }

@router.get("/{analysis_id}/risks")
async def get_analysis_risks(
    analysis_id: str,
    category: Optional[RiskCategory] = None,
    severity: Optional[RiskSeverity] = None,
    db: Session = Depends(get_db)
):
    """Get risks for an analysis with optional filtering"""
    analysis = db.query(AnalysisModel).filter(
        AnalysisModel.analysis_id == analysis_id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")

    query = db.query(RiskModel).filter(RiskModel.analysis_id == analysis.id)

    if category:
        query = query.filter(RiskModel.category == category)
    if severity:
        query = query.filter(RiskModel.severity == severity)

    risks = query.all()

    return {
        "analysis_id": analysis_id,
        "total": len(risks),
        "risks": risks
    }

@router.delete("/{analysis_id}")
async def delete_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """Delete an analysis and its associated risks"""
    analysis = db.query(AnalysisModel).filter(
        AnalysisModel.analysis_id == analysis_id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")

    # Delete associated risks
    db.query(RiskModel).filter(RiskModel.analysis_id == analysis.id).delete()

    # Delete document associations
    db.query(AnalysisDocuments).filter(AnalysisDocuments.analysis_id == analysis.id).delete()

    # Delete analysis
    db.delete(analysis)
    db.commit()

    return {"message": f"Analysis {analysis_id} deleted successfully"}
