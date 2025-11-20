# routers/dashboard.py - Dashboard and statistics endpoints
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import (
    DocumentModel, AnalysisModel, RiskModel, AnalysisStatus,
    RiskSeverity, RiskCategory, RiskLikelihood,
    DashboardStats, RiskSummary, AnalysisResponse, AnalysisDocuments
)

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""

    # Count documents
    total_documents = db.query(DocumentModel).count()

    # Count analyses
    total_analyses = db.query(AnalysisModel).count()
    completed_analyses = db.query(AnalysisModel).filter(
        AnalysisModel.status == AnalysisStatus.COMPLETED
    ).count()

    # Count and summarize risks
    total_risks = db.query(RiskModel).count()

    # By severity
    by_severity = {
        "Critical": db.query(RiskModel).filter(RiskModel.severity == RiskSeverity.CRITICAL).count(),
        "High": db.query(RiskModel).filter(RiskModel.severity == RiskSeverity.HIGH).count(),
        "Medium": db.query(RiskModel).filter(RiskModel.severity == RiskSeverity.MEDIUM).count(),
        "Low": db.query(RiskModel).filter(RiskModel.severity == RiskSeverity.LOW).count(),
    }

    # By category
    by_category = {
        "Contractual": db.query(RiskModel).filter(RiskModel.category == RiskCategory.CONTRACTUAL).count(),
        "Regulatory": db.query(RiskModel).filter(RiskModel.category == RiskCategory.REGULATORY).count(),
        "Litigation": db.query(RiskModel).filter(RiskModel.category == RiskCategory.LITIGATION).count(),
        "IP": db.query(RiskModel).filter(RiskModel.category == RiskCategory.IP).count(),
        "Operational": db.query(RiskModel).filter(RiskModel.category == RiskCategory.OPERATIONAL).count(),
    }

    # By likelihood
    by_likelihood = {
        "Very Likely": db.query(RiskModel).filter(RiskModel.likelihood == RiskLikelihood.VERY_LIKELY).count(),
        "Likely": db.query(RiskModel).filter(RiskModel.likelihood == RiskLikelihood.LIKELY).count(),
        "Possible": db.query(RiskModel).filter(RiskModel.likelihood == RiskLikelihood.POSSIBLE).count(),
        "Unlikely": db.query(RiskModel).filter(RiskModel.likelihood == RiskLikelihood.UNLIKELY).count(),
    }

    risk_summary = RiskSummary(
        total=total_risks,
        by_severity=by_severity,
        by_category=by_category,
        by_likelihood=by_likelihood
    )

    # Recent analyses
    recent = db.query(AnalysisModel).order_by(
        AnalysisModel.created_at.desc()
    ).limit(5).all()

    recent_analyses = []
    for analysis in recent:
        doc_count = db.query(AnalysisDocuments).filter(
            AnalysisDocuments.analysis_id == analysis.id
        ).count()
        risk_count = db.query(RiskModel).filter(
            RiskModel.analysis_id == analysis.id
        ).count()

        recent_analyses.append(AnalysisResponse(
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

    return DashboardStats(
        total_documents=total_documents,
        total_analyses=total_analyses,
        completed_analyses=completed_analyses,
        total_risks=total_risks,
        risk_summary=risk_summary,
        recent_analyses=recent_analyses
    )

@router.get("/risk-matrix")
async def get_risk_matrix(db: Session = Depends(get_db)):
    """Get risk matrix data for visualization"""

    risks = db.query(RiskModel).all()

    # Create matrix data
    matrix = {}
    for risk in risks:
        severity = risk.severity.value if hasattr(risk.severity, 'value') else risk.severity
        likelihood = risk.likelihood.value if hasattr(risk.likelihood, 'value') else risk.likelihood

        key = f"{severity}_{likelihood}"
        if key not in matrix:
            matrix[key] = {
                "severity": severity,
                "likelihood": likelihood,
                "count": 0,
                "risks": []
            }
        matrix[key]["count"] += 1
        matrix[key]["risks"].append({
            "risk_id": risk.risk_id,
            "title": risk.title,
            "category": risk.category.value if hasattr(risk.category, 'value') else risk.category
        })

    return {
        "matrix": list(matrix.values()),
        "severities": ["Critical", "High", "Medium", "Low"],
        "likelihoods": ["Very Likely", "Likely", "Possible", "Unlikely"]
    }

@router.get("/category-breakdown")
async def get_category_breakdown(db: Session = Depends(get_db)):
    """Get risk breakdown by category with severity distribution"""

    categories = ["Contractual", "Regulatory", "Litigation", "IP", "Operational"]
    breakdown = []

    for category in categories:
        category_enum = RiskCategory(category)
        risks = db.query(RiskModel).filter(RiskModel.category == category_enum).all()

        severity_dist = {
            "Critical": 0,
            "High": 0,
            "Medium": 0,
            "Low": 0
        }

        for risk in risks:
            severity = risk.severity.value if hasattr(risk.severity, 'value') else risk.severity
            if severity in severity_dist:
                severity_dist[severity] += 1

        breakdown.append({
            "category": category,
            "total": len(risks),
            "by_severity": severity_dist
        })

    return breakdown

@router.get("/timeline")
async def get_analysis_timeline(db: Session = Depends(get_db)):
    """Get analysis timeline for trending"""

    analyses = db.query(AnalysisModel).order_by(
        AnalysisModel.created_at.asc()
    ).all()

    timeline = []
    for analysis in analyses:
        risk_count = db.query(RiskModel).filter(
            RiskModel.analysis_id == analysis.id
        ).count()

        timeline.append({
            "analysis_id": analysis.analysis_id,
            "name": analysis.name,
            "date": analysis.created_at.isoformat() if analysis.created_at else None,
            "status": analysis.status.value if hasattr(analysis.status, 'value') else analysis.status,
            "risk_count": risk_count
        })

    return timeline
