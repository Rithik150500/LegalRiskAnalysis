"""
Data models for Legal Risk Analysis system.
"""

from .data_room import (
    Page,
    Document,
    DataRoom,
    DocumentType,
    RiskLevel,
    RiskFinding,
    LegalRiskAnalysisReport
)

__all__ = [
    "Page",
    "Document",
    "DataRoom",
    "DocumentType",
    "RiskLevel",
    "RiskFinding",
    "LegalRiskAnalysisReport"
]
