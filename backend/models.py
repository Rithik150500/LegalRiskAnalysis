# models.py - Pydantic models and SQLAlchemy ORM models
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

# Enums
class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class RiskSeverity(str, enum.Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class RiskLikelihood(str, enum.Enum):
    VERY_LIKELY = "Very Likely"
    LIKELY = "Likely"
    POSSIBLE = "Possible"
    UNLIKELY = "Unlikely"

class RiskCategory(str, enum.Enum):
    CONTRACTUAL = "Contractual"
    REGULATORY = "Regulatory"
    LITIGATION = "Litigation"
    IP = "IP"
    OPERATIONAL = "Operational"

# SQLAlchemy ORM Models
class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String(50), unique=True, index=True)
    filename = Column(String(255))
    original_filename = Column(String(255))
    file_path = Column(String(500))
    file_type = Column(String(50))
    file_size = Column(Integer)
    summary = Column(Text)
    page_count = Column(Integer, default=0)
    pages_data = Column(JSON)  # Store page summaries and metadata
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    analyses = relationship("AnalysisModel", back_populates="documents", secondary="analysis_documents")

class AnalysisModel(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String(50), unique=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    progress = Column(Integer, default=0)
    current_step = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    result_data = Column(JSON)  # Store the full analysis result
    report_path = Column(String(500))
    dashboard_path = Column(String(500))

    documents = relationship("DocumentModel", back_populates="analyses", secondary="analysis_documents")
    risks = relationship("RiskModel", back_populates="analysis")

class AnalysisDocuments(Base):
    __tablename__ = "analysis_documents"

    analysis_id = Column(Integer, ForeignKey("analyses.id"), primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), primary_key=True)

class RiskModel(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(String(50), index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"))
    category = Column(SQLEnum(RiskCategory))
    title = Column(String(255))
    description = Column(Text)
    severity = Column(SQLEnum(RiskSeverity))
    likelihood = Column(SQLEnum(RiskLikelihood))
    evidence = Column(JSON)  # List of evidence items
    legal_basis = Column(Text)
    recommended_mitigation = Column(Text)

    analysis = relationship("AnalysisModel", back_populates="risks")

# Pydantic Models for API
class DocumentBase(BaseModel):
    filename: str
    summary: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(BaseModel):
    id: int
    doc_id: str
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    summary: Optional[str]
    page_count: int
    uploaded_at: datetime

    class Config:
        from_attributes = True

class DocumentDetail(DocumentResponse):
    pages_data: Optional[List[Dict[str, Any]]] = None
    file_path: str

class EvidenceItem(BaseModel):
    doc_id: str
    page_num: int
    citation: str

class RiskBase(BaseModel):
    risk_id: str
    category: RiskCategory
    title: str
    description: str
    severity: RiskSeverity
    likelihood: RiskLikelihood
    evidence: List[EvidenceItem]
    legal_basis: str
    recommended_mitigation: str

class RiskResponse(RiskBase):
    id: int

    class Config:
        from_attributes = True

class AnalysisCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    document_ids: List[str]
    risk_categories: Optional[List[RiskCategory]] = None

class AnalysisResponse(BaseModel):
    id: int
    analysis_id: str
    name: str
    description: Optional[str]
    status: AnalysisStatus
    progress: int
    current_step: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    document_count: int = 0
    risk_count: int = 0

    class Config:
        from_attributes = True

class AnalysisDetail(AnalysisResponse):
    result_data: Optional[Dict[str, Any]]
    report_path: Optional[str]
    dashboard_path: Optional[str]
    documents: List[DocumentResponse] = []
    risks: List[RiskResponse] = []

class AnalysisStatusUpdate(BaseModel):
    status: AnalysisStatus
    progress: Optional[int] = None
    current_step: Optional[str] = None
    error_message: Optional[str] = None

class RiskSummary(BaseModel):
    total: int
    by_severity: Dict[str, int]
    by_category: Dict[str, int]
    by_likelihood: Dict[str, int]

class DashboardStats(BaseModel):
    total_documents: int
    total_analyses: int
    completed_analyses: int
    total_risks: int
    risk_summary: RiskSummary
    recent_analyses: List[AnalysisResponse]
