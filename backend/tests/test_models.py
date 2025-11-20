# test_models.py - Tests for Pydantic models and enums
import pytest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    AnalysisStatus, RiskSeverity, RiskLikelihood, RiskCategory,
    DocumentBase, DocumentCreate, DocumentResponse, DocumentDetail,
    EvidenceItem, RiskBase, RiskResponse,
    AnalysisCreate, AnalysisResponse, AnalysisDetail,
    RiskSummary, DashboardStats
)


class TestEnums:
    """Test enum values and string representations"""

    def test_analysis_status_values(self):
        """Test AnalysisStatus enum values"""
        assert AnalysisStatus.PENDING == "pending"
        assert AnalysisStatus.RUNNING == "running"
        assert AnalysisStatus.COMPLETED == "completed"
        assert AnalysisStatus.FAILED == "failed"

    def test_risk_severity_values(self):
        """Test RiskSeverity enum values"""
        assert RiskSeverity.CRITICAL == "Critical"
        assert RiskSeverity.HIGH == "High"
        assert RiskSeverity.MEDIUM == "Medium"
        assert RiskSeverity.LOW == "Low"

    def test_risk_likelihood_values(self):
        """Test RiskLikelihood enum values"""
        assert RiskLikelihood.VERY_LIKELY == "Very Likely"
        assert RiskLikelihood.LIKELY == "Likely"
        assert RiskLikelihood.POSSIBLE == "Possible"
        assert RiskLikelihood.UNLIKELY == "Unlikely"

    def test_risk_category_values(self):
        """Test RiskCategory enum values"""
        assert RiskCategory.CONTRACTUAL == "Contractual"
        assert RiskCategory.REGULATORY == "Regulatory"
        assert RiskCategory.LITIGATION == "Litigation"
        assert RiskCategory.IP == "IP"
        assert RiskCategory.OPERATIONAL == "Operational"

    def test_enum_membership(self):
        """Test enum membership"""
        assert "pending" in [s.value for s in AnalysisStatus]
        assert "Critical" in [s.value for s in RiskSeverity]
        assert "Contractual" in [c.value for c in RiskCategory]


class TestDocumentModels:
    """Test Document Pydantic models"""

    def test_document_base_creation(self):
        """Test DocumentBase model creation"""
        doc = DocumentBase(filename="test.pdf", summary="Test summary")
        assert doc.filename == "test.pdf"
        assert doc.summary == "Test summary"

    def test_document_base_optional_summary(self):
        """Test DocumentBase with optional summary"""
        doc = DocumentBase(filename="test.pdf")
        assert doc.filename == "test.pdf"
        assert doc.summary is None

    def test_document_create_inherits_base(self):
        """Test DocumentCreate inherits from DocumentBase"""
        doc = DocumentCreate(filename="test.pdf", summary="Summary")
        assert doc.filename == "test.pdf"
        assert doc.summary == "Summary"

    def test_document_response_creation(self):
        """Test DocumentResponse model creation"""
        now = datetime.utcnow()
        doc = DocumentResponse(
            id=1,
            doc_id="DOC12345678",
            filename="stored_name.pdf",
            original_filename="original.pdf",
            file_type="PDF",
            file_size=1024,
            summary="Test summary",
            page_count=5,
            uploaded_at=now
        )
        assert doc.id == 1
        assert doc.doc_id == "DOC12345678"
        assert doc.page_count == 5
        assert doc.uploaded_at == now

    def test_document_detail_extends_response(self):
        """Test DocumentDetail extends DocumentResponse"""
        now = datetime.utcnow()
        pages = [{"page_num": 1, "summdesc": "Page 1"}]
        doc = DocumentDetail(
            id=1,
            doc_id="DOC12345678",
            filename="stored_name.pdf",
            original_filename="original.pdf",
            file_type="PDF",
            file_size=1024,
            summary="Test summary",
            page_count=1,
            uploaded_at=now,
            pages_data=pages,
            file_path="/uploads/DOC12345678.pdf"
        )
        assert doc.pages_data == pages
        assert doc.file_path == "/uploads/DOC12345678.pdf"


class TestEvidenceItem:
    """Test EvidenceItem model"""

    def test_evidence_item_creation(self):
        """Test EvidenceItem creation"""
        evidence = EvidenceItem(
            doc_id="DOC12345678",
            page_num=5,
            citation="Section 3.2: Liability clause"
        )
        assert evidence.doc_id == "DOC12345678"
        assert evidence.page_num == 5
        assert evidence.citation == "Section 3.2: Liability clause"

    def test_evidence_item_validation(self):
        """Test EvidenceItem requires all fields"""
        with pytest.raises(Exception):
            EvidenceItem(doc_id="DOC123")  # Missing required fields


class TestRiskModels:
    """Test Risk Pydantic models"""

    def test_risk_base_creation(self):
        """Test RiskBase model creation"""
        evidence = [
            EvidenceItem(doc_id="DOC123", page_num=1, citation="Test citation")
        ]
        risk = RiskBase(
            risk_id="RISK_001",
            category=RiskCategory.CONTRACTUAL,
            title="Test Risk",
            description="Test description",
            severity=RiskSeverity.HIGH,
            likelihood=RiskLikelihood.LIKELY,
            evidence=evidence,
            legal_basis="Contract Law",
            recommended_mitigation="Review contract"
        )
        assert risk.risk_id == "RISK_001"
        assert risk.category == RiskCategory.CONTRACTUAL
        assert risk.severity == RiskSeverity.HIGH
        assert len(risk.evidence) == 1

    def test_risk_response_extends_base(self):
        """Test RiskResponse extends RiskBase with id"""
        evidence = [
            EvidenceItem(doc_id="DOC123", page_num=1, citation="Citation")
        ]
        risk = RiskResponse(
            id=1,
            risk_id="RISK_001",
            category=RiskCategory.REGULATORY,
            title="Compliance Risk",
            description="GDPR compliance issue",
            severity=RiskSeverity.CRITICAL,
            likelihood=RiskLikelihood.VERY_LIKELY,
            evidence=evidence,
            legal_basis="GDPR",
            recommended_mitigation="Implement DPA"
        )
        assert risk.id == 1
        assert risk.risk_id == "RISK_001"


class TestAnalysisModels:
    """Test Analysis Pydantic models"""

    def test_analysis_create_with_required_fields(self):
        """Test AnalysisCreate with required fields"""
        analysis = AnalysisCreate(
            name="Test Analysis",
            document_ids=["DOC123", "DOC456"]
        )
        assert analysis.name == "Test Analysis"
        assert analysis.description == ""
        assert len(analysis.document_ids) == 2
        assert analysis.risk_categories is None

    def test_analysis_create_with_all_fields(self):
        """Test AnalysisCreate with all optional fields"""
        analysis = AnalysisCreate(
            name="Full Analysis",
            description="Complete analysis",
            document_ids=["DOC123"],
            risk_categories=[RiskCategory.CONTRACTUAL, RiskCategory.REGULATORY]
        )
        assert analysis.description == "Complete analysis"
        assert len(analysis.risk_categories) == 2

    def test_analysis_response_creation(self):
        """Test AnalysisResponse model creation"""
        now = datetime.utcnow()
        response = AnalysisResponse(
            id=1,
            analysis_id="ANA12345678",
            name="Test Analysis",
            description="Description",
            status=AnalysisStatus.COMPLETED,
            progress=100,
            current_step="Complete",
            created_at=now,
            started_at=now,
            completed_at=now,
            error_message=None,
            document_count=2,
            risk_count=5
        )
        assert response.analysis_id == "ANA12345678"
        assert response.status == AnalysisStatus.COMPLETED
        assert response.progress == 100
        assert response.document_count == 2
        assert response.risk_count == 5

    def test_analysis_detail_extends_response(self):
        """Test AnalysisDetail extends AnalysisResponse"""
        now = datetime.utcnow()
        detail = AnalysisDetail(
            id=1,
            analysis_id="ANA12345678",
            name="Test Analysis",
            description="Description",
            status=AnalysisStatus.COMPLETED,
            progress=100,
            current_step="Complete",
            created_at=now,
            started_at=now,
            completed_at=now,
            error_message=None,
            document_count=1,
            risk_count=2,
            result_data={"key": "value"},
            report_path="/outputs/report.docx",
            dashboard_path="/outputs/dashboard.html",
            documents=[],
            risks=[]
        )
        assert detail.result_data == {"key": "value"}
        assert detail.report_path == "/outputs/report.docx"


class TestDashboardModels:
    """Test Dashboard Pydantic models"""

    def test_risk_summary_creation(self):
        """Test RiskSummary model creation"""
        summary = RiskSummary(
            total=10,
            by_severity={"Critical": 1, "High": 3, "Medium": 4, "Low": 2},
            by_category={"Contractual": 5, "Regulatory": 3, "Litigation": 2},
            by_likelihood={"Very Likely": 2, "Likely": 3, "Possible": 3, "Unlikely": 2}
        )
        assert summary.total == 10
        assert summary.by_severity["Critical"] == 1
        assert summary.by_category["Contractual"] == 5

    def test_dashboard_stats_creation(self):
        """Test DashboardStats model creation"""
        risk_summary = RiskSummary(
            total=5,
            by_severity={"Critical": 0, "High": 2, "Medium": 2, "Low": 1},
            by_category={"Contractual": 3, "Regulatory": 2},
            by_likelihood={"Likely": 3, "Possible": 2}
        )
        stats = DashboardStats(
            total_documents=10,
            total_analyses=5,
            completed_analyses=3,
            total_risks=5,
            risk_summary=risk_summary,
            recent_analyses=[]
        )
        assert stats.total_documents == 10
        assert stats.total_analyses == 5
        assert stats.completed_analyses == 3
        assert stats.risk_summary.total == 5


class TestModelValidation:
    """Test model validation behavior"""

    def test_document_base_requires_filename(self):
        """Test DocumentBase requires filename"""
        with pytest.raises(Exception):
            DocumentBase()

    def test_analysis_create_requires_name_and_docs(self):
        """Test AnalysisCreate requires name and document_ids"""
        with pytest.raises(Exception):
            AnalysisCreate(name="Test")  # Missing document_ids

        with pytest.raises(Exception):
            AnalysisCreate(document_ids=["DOC123"])  # Missing name

    def test_evidence_item_requires_all_fields(self):
        """Test EvidenceItem requires all fields"""
        with pytest.raises(Exception):
            EvidenceItem(doc_id="DOC123", page_num=1)  # Missing citation

    def test_invalid_enum_value_raises_error(self):
        """Test invalid enum values raise errors"""
        with pytest.raises(Exception):
            AnalysisCreate(
                name="Test",
                document_ids=["DOC123"],
                risk_categories=["InvalidCategory"]
            )
