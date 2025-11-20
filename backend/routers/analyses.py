# routers/analyses.py - Analysis management endpoints
import os
import sys
import uuid
import json
import asyncio
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import get_db
from models import (
    AnalysisModel, AnalysisStatus, DocumentModel, RiskModel,
    AnalysisCreate, AnalysisResponse, AnalysisDetail, AnalysisDocuments,
    RiskCategory, RiskSeverity, RiskLikelihood
)
from services.analysis_service import create_analysis_service
from services.report_generator import create_report_generator
from services.dashboard_generator import create_dashboard_generator

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

        # Progress tracking
        import time

        # Phase 1: Load documents
        analysis.current_step = "Loading documents..."
        analysis.progress = 10
        db.commit()
        time.sleep(0.3)

        # Prepare document data for analysis
        docs_data = []
        for doc in documents:
            docs_data.append({
                "doc_id": doc.doc_id,
                "original_filename": doc.original_filename,
                "summary": doc.summary,
                "page_count": doc.page_count,
                "pages_data": doc.pages_data
            })

        # Phase 2: Run AI analysis
        analysis.current_step = "Analyzing documents with AI..."
        analysis.progress = 20
        db.commit()

        # Create analysis service and run analysis
        analysis_service = create_analysis_service()

        # Update progress during analysis phases
        phases = [
            ("Analyzing contractual risks...", 30),
            ("Analyzing regulatory compliance...", 45),
            ("Analyzing litigation exposure...", 55),
            ("Analyzing IP concerns...", 65),
            ("Analyzing operational risks...", 75),
        ]

        for step, progress in phases:
            analysis.current_step = step
            analysis.progress = progress
            db.commit()
            time.sleep(0.3)

        # Perform the actual analysis
        analysis_result = analysis_service.analyze_documents(docs_data)

        analysis.current_step = "Processing analysis results..."
        analysis.progress = 80
        db.commit()

        # Extract risks from analysis result
        risks_data = analysis_result.get("risks", [])
        analysis_summary = analysis_result.get("analysis_summary", f"Analysis of {len(documents)} documents")

        # Save risks to database
        for risk_data in risks_data:
            # Map string severity/likelihood to enums
            severity_map = {
                "Critical": RiskSeverity.CRITICAL,
                "High": RiskSeverity.HIGH,
                "Medium": RiskSeverity.MEDIUM,
                "Low": RiskSeverity.LOW
            }
            likelihood_map = {
                "Very Likely": RiskLikelihood.VERY_LIKELY,
                "Likely": RiskLikelihood.LIKELY,
                "Possible": RiskLikelihood.POSSIBLE,
                "Unlikely": RiskLikelihood.UNLIKELY
            }
            category_map = {
                "Contractual": RiskCategory.CONTRACTUAL,
                "Regulatory": RiskCategory.REGULATORY,
                "Litigation": RiskCategory.LITIGATION,
                "IP": RiskCategory.IP,
                "Operational": RiskCategory.OPERATIONAL
            }

            db_risk = RiskModel(
                risk_id=risk_data.get("risk_id", f"RISK_{uuid.uuid4().hex[:6].upper()}"),
                analysis_id=analysis.id,
                category=category_map.get(risk_data.get("category", "Operational"), RiskCategory.OPERATIONAL),
                title=risk_data.get("title", "Untitled Risk"),
                description=risk_data.get("description", ""),
                severity=severity_map.get(risk_data.get("severity", "Medium"), RiskSeverity.MEDIUM),
                likelihood=likelihood_map.get(risk_data.get("likelihood", "Possible"), RiskLikelihood.POSSIBLE),
                evidence=risk_data.get("evidence", []),
                legal_basis=risk_data.get("legal_basis", ""),
                recommended_mitigation=risk_data.get("recommended_mitigation", "")
            )
            db.add(db_risk)

        db.commit()

        # Phase 3: Generate report
        analysis.current_step = "Generating Word report..."
        analysis.progress = 85
        db.commit()

        # Define output paths
        outputs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")
        os.makedirs(outputs_dir, exist_ok=True)

        report_filename = f"{analysis_id}_report.docx"
        dashboard_filename = f"{analysis_id}_dashboard.html"
        report_path = os.path.join(outputs_dir, report_filename)
        dashboard_path = os.path.join(outputs_dir, dashboard_filename)

        # Generate Word report
        report_generator = create_report_generator()
        report_generator.generate_report(
            analysis_id=analysis_id,
            analysis_name=analysis.name,
            analysis_summary=analysis_summary,
            documents=docs_data,
            risks=risks_data,
            output_path=report_path
        )

        # Phase 4: Generate dashboard
        analysis.current_step = "Generating interactive dashboard..."
        analysis.progress = 95
        db.commit()

        # Generate HTML dashboard
        dashboard_generator = create_dashboard_generator()
        dashboard_generator.generate_dashboard(
            analysis_id=analysis_id,
            analysis_name=analysis.name,
            analysis_summary=analysis_summary,
            documents=docs_data,
            risks=risks_data,
            output_path=dashboard_path
        )

        # Store result data
        result_data = {
            "analysis_summary": analysis_summary,
            "documents_analyzed": document_ids,
            "total_risks": len(risks_data),
            "by_severity": {
                "Critical": len([r for r in risks_data if r.get("severity") == "Critical"]),
                "High": len([r for r in risks_data if r.get("severity") == "High"]),
                "Medium": len([r for r in risks_data if r.get("severity") == "Medium"]),
                "Low": len([r for r in risks_data if r.get("severity") == "Low"]),
            },
            "by_category": {
                "Contractual": len([r for r in risks_data if r.get("category") == "Contractual"]),
                "Regulatory": len([r for r in risks_data if r.get("category") == "Regulatory"]),
                "Litigation": len([r for r in risks_data if r.get("category") == "Litigation"]),
                "IP": len([r for r in risks_data if r.get("category") == "IP"]),
                "Operational": len([r for r in risks_data if r.get("category") == "Operational"]),
            }
        }

        # Update analysis as completed
        analysis.status = AnalysisStatus.COMPLETED
        analysis.completed_at = datetime.utcnow()
        analysis.progress = 100
        analysis.current_step = "Analysis complete"
        analysis.result_data = result_data
        analysis.report_path = f"/api/analyses/{analysis_id}/download/report"
        analysis.dashboard_path = f"/api/analyses/{analysis_id}/download/dashboard"
        db.commit()

    except Exception as e:
        # Handle errors
        import traceback
        print(f"Analysis error: {e}")
        print(traceback.format_exc())
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


@router.get("/{analysis_id}/download/report")
async def download_report(analysis_id: str, db: Session = Depends(get_db)):
    """Download the Word report for an analysis"""
    analysis = db.query(AnalysisModel).filter(
        AnalysisModel.analysis_id == analysis_id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")

    if analysis.status != AnalysisStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Analysis is not yet completed")

    # Build file path
    outputs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")
    report_filename = f"{analysis_id}_report.docx"
    report_path = os.path.join(outputs_dir, report_filename)

    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        path=report_path,
        filename=f"{analysis.name.replace(' ', '_')}_Legal_Risk_Report.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@router.get("/{analysis_id}/download/dashboard")
async def download_dashboard(analysis_id: str, db: Session = Depends(get_db)):
    """Download the interactive HTML dashboard for an analysis"""
    analysis = db.query(AnalysisModel).filter(
        AnalysisModel.analysis_id == analysis_id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")

    if analysis.status != AnalysisStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Analysis is not yet completed")

    # Build file path
    outputs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")
    dashboard_filename = f"{analysis_id}_dashboard.html"
    dashboard_path = os.path.join(outputs_dir, dashboard_filename)

    if not os.path.exists(dashboard_path):
        raise HTTPException(status_code=404, detail="Dashboard file not found")

    return FileResponse(
        path=dashboard_path,
        filename=f"{analysis.name.replace(' ', '_')}_Legal_Risk_Dashboard.html",
        media_type="text/html"
    )
