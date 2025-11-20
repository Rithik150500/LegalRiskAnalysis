"""
Legal Risk Analysis System

A comprehensive system for analyzing legal documents and identifying risks
using Claude's Deep Agent architecture with specialized subagents.
"""

__version__ = "1.0.0"

from .config import get_config, SystemConfig
from .models import (
    DataRoom,
    Document,
    Page,
    DocumentType,
    RiskLevel,
    RiskFinding,
    LegalRiskAnalysisReport
)
from .tools import (
    DataRoomTools,
    create_data_room_tools,
    WebResearchTools,
    create_web_research_tools
)
from .agents import (
    MainLegalRiskAnalysisAgent,
    create_main_agent,
    get_analysis_subagent_config,
    get_report_subagent_config,
    get_dashboard_subagent_config
)
from .main import run_analysis, create_sample_data_room, load_data_room

__all__ = [
    # Version
    "__version__",
    # Config
    "get_config",
    "SystemConfig",
    # Models
    "DataRoom",
    "Document",
    "Page",
    "DocumentType",
    "RiskLevel",
    "RiskFinding",
    "LegalRiskAnalysisReport",
    # Tools
    "DataRoomTools",
    "create_data_room_tools",
    "WebResearchTools",
    "create_web_research_tools",
    # Agents
    "MainLegalRiskAnalysisAgent",
    "create_main_agent",
    "get_analysis_subagent_config",
    "get_report_subagent_config",
    "get_dashboard_subagent_config",
    # Main functions
    "run_analysis",
    "create_sample_data_room",
    "load_data_room"
]
