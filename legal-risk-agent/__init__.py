# Legal Risk Analysis Deep Agent System
"""
A multi-agent system for comprehensive legal risk analysis using Claude.

This package provides:
- DataRoom: Document storage and retrieval for legal documents
- Analysis Subagent: Deep document analysis for risk identification
- Report Subagent: Professional Word document generation
- Dashboard Subagent: Interactive HTML dashboard creation
- Main Agent: Orchestration and coordination of the analysis workflow
"""

from .data_room_tools import DataRoom, create_data_room_tools
from .web_research_tools import create_web_research_tools
from .main_agent import create_legal_risk_analysis_agent

__version__ = "1.0.0"
__all__ = [
    "DataRoom",
    "create_data_room_tools",
    "create_web_research_tools",
    "create_legal_risk_analysis_agent"
]
