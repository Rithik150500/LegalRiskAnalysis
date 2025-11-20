"""
Data Room Models for Legal Risk Analysis

This module defines the data structures for the Data Room containing
legal documents with hierarchical organization (documents -> pages).
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid
import base64


class DocumentType(Enum):
    """Types of legal documents in the data room."""
    CONTRACT = "contract"
    AGREEMENT = "agreement"
    DISCLOSURE = "disclosure"
    REGULATORY = "regulatory"
    COMPLIANCE = "compliance"
    LITIGATION = "litigation"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    CORPORATE = "corporate"
    FINANCIAL = "financial"
    OTHER = "other"


class RiskLevel(Enum):
    """Risk levels for legal analysis."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


@dataclass
class Page:
    """
    Represents a single page within a document.

    Attributes:
        page_num: The page number (1-indexed)
        summdesc: Summary description of the page content
        page_image: Base64 encoded image of the page (optional)
        extracted_text: OCR or extracted text from the page
        metadata: Additional page-level metadata
    """
    page_num: int
    summdesc: str
    page_image: Optional[str] = None  # Base64 encoded image
    extracted_text: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert page to dictionary representation."""
        return {
            "page_num": self.page_num,
            "summdesc": self.summdesc,
            "page_image": self.page_image,
            "extracted_text": self.extracted_text,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Page":
        """Create a Page instance from a dictionary."""
        return cls(
            page_num=data["page_num"],
            summdesc=data["summdesc"],
            page_image=data.get("page_image"),
            extracted_text=data.get("extracted_text"),
            metadata=data.get("metadata", {})
        )


@dataclass
class Document:
    """
    Represents a legal document in the data room.

    Attributes:
        doc_id: Unique identifier for the document
        summdesc: Summary description of the entire document
        pages: List of pages in the document
        document_type: Type of legal document
        title: Document title
        source: Source or origin of the document
        date_added: When the document was added to the data room
        metadata: Additional document-level metadata
    """
    doc_id: str
    summdesc: str
    pages: List[Page] = field(default_factory=list)
    document_type: DocumentType = DocumentType.OTHER
    title: Optional[str] = None
    source: Optional[str] = None
    date_added: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Generate doc_id if not provided."""
        if not self.doc_id:
            self.doc_id = str(uuid.uuid4())

    def get_combined_summary(self) -> str:
        """
        Get combined summary description of all pages.

        Returns:
            Combined summary of all page descriptions.
        """
        if not self.pages:
            return self.summdesc

        page_summaries = [
            f"Page {page.page_num}: {page.summdesc}"
            for page in sorted(self.pages, key=lambda p: p.page_num)
        ]

        return f"{self.summdesc}\n\nPage Details:\n" + "\n".join(page_summaries)

    def get_page(self, page_num: int) -> Optional[Page]:
        """Get a specific page by page number."""
        for page in self.pages:
            if page.page_num == page_num:
                return page
        return None

    def get_pages(self, page_nums: List[int]) -> List[Page]:
        """Get multiple pages by page numbers."""
        return [
            page for page in self.pages
            if page.page_num in page_nums
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary representation."""
        return {
            "doc_id": self.doc_id,
            "summdesc": self.summdesc,
            "pages": [page.to_dict() for page in self.pages],
            "document_type": self.document_type.value,
            "title": self.title,
            "source": self.source,
            "date_added": self.date_added,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Create a Document instance from a dictionary."""
        pages = [Page.from_dict(p) for p in data.get("pages", [])]
        doc_type = DocumentType(data.get("document_type", "other"))

        return cls(
            doc_id=data["doc_id"],
            summdesc=data["summdesc"],
            pages=pages,
            document_type=doc_type,
            title=data.get("title"),
            source=data.get("source"),
            date_added=data.get("date_added"),
            metadata=data.get("metadata", {})
        )


@dataclass
class DataRoom:
    """
    Represents the complete data room containing all documents.

    Attributes:
        documents: List of documents in the data room
        name: Name of the data room
        description: Description of the data room purpose
        metadata: Additional data room metadata
    """
    documents: List[Document] = field(default_factory=list)
    name: str = "Legal Data Room"
    description: str = "Data room for legal risk analysis"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_document(self, document: Document) -> None:
        """Add a document to the data room."""
        self.documents.append(document)

    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a document by its ID."""
        for doc in self.documents:
            if doc.doc_id == doc_id:
                return doc
        return None

    def get_document_index(self) -> List[Dict[str, str]]:
        """
        Get the data room index with document summaries.

        Returns:
            List of dictionaries with doc_id and summdesc for each document.
        """
        return [
            {
                "doc_id": doc.doc_id,
                "summdesc": doc.summdesc,
                "title": doc.title,
                "document_type": doc.document_type.value
            }
            for doc in self.documents
        ]

    def get_summary_index(self) -> List[Dict[str, str]]:
        """
        Get simplified index with just summaries (for user content).

        Returns:
            List of dictionaries with just summdesc for each document.
        """
        return [
            {"summdesc": doc.summdesc}
            for doc in self.documents
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert data room to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "documents": [doc.to_dict() for doc in self.documents],
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataRoom":
        """Create a DataRoom instance from a dictionary."""
        documents = [Document.from_dict(d) for d in data.get("documents", [])]

        return cls(
            documents=documents,
            name=data.get("name", "Legal Data Room"),
            description=data.get("description", ""),
            metadata=data.get("metadata", {})
        )


@dataclass
class RiskFinding:
    """
    Represents a single risk finding from analysis.

    Attributes:
        risk_id: Unique identifier for the risk
        title: Short title describing the risk
        description: Detailed description of the risk
        risk_level: Severity level of the risk
        source_doc_id: Document ID where risk was identified
        source_pages: Page numbers where risk was found
        category: Risk category
        recommendations: Suggested actions to mitigate
        legal_references: Relevant legal citations or precedents
    """
    risk_id: str
    title: str
    description: str
    risk_level: RiskLevel
    source_doc_id: str
    source_pages: List[int] = field(default_factory=list)
    category: str = "General"
    recommendations: List[str] = field(default_factory=list)
    legal_references: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Generate risk_id if not provided."""
        if not self.risk_id:
            self.risk_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert risk finding to dictionary."""
        return {
            "risk_id": self.risk_id,
            "title": self.title,
            "description": self.description,
            "risk_level": self.risk_level.value,
            "source_doc_id": self.source_doc_id,
            "source_pages": self.source_pages,
            "category": self.category,
            "recommendations": self.recommendations,
            "legal_references": self.legal_references,
            "metadata": self.metadata
        }


@dataclass
class LegalRiskAnalysisReport:
    """
    Complete legal risk analysis report.

    Attributes:
        report_id: Unique identifier for the report
        title: Report title
        executive_summary: High-level summary of findings
        findings: List of risk findings
        data_room_name: Name of analyzed data room
        analysis_date: Date of analysis
        methodology: Description of analysis methodology
        conclusions: Overall conclusions
        next_steps: Recommended next steps
    """
    report_id: str
    title: str
    executive_summary: str
    findings: List[RiskFinding] = field(default_factory=list)
    data_room_name: str = ""
    analysis_date: str = ""
    methodology: str = ""
    conclusions: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Generate report_id if not provided."""
        if not self.report_id:
            self.report_id = str(uuid.uuid4())

    def get_risk_summary(self) -> Dict[str, int]:
        """Get count of risks by severity level."""
        summary = {level.value: 0 for level in RiskLevel}
        for finding in self.findings:
            summary[finding.risk_level.value] += 1
        return summary

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "report_id": self.report_id,
            "title": self.title,
            "executive_summary": self.executive_summary,
            "findings": [f.to_dict() for f in self.findings],
            "data_room_name": self.data_room_name,
            "analysis_date": self.analysis_date,
            "methodology": self.methodology,
            "conclusions": self.conclusions,
            "next_steps": self.next_steps,
            "risk_summary": self.get_risk_summary(),
            "metadata": self.metadata
        }
