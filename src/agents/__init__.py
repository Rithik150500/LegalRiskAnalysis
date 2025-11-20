"""
Agents for Legal Risk Analysis system.
"""

from .main_agent import (
    MainLegalRiskAnalysisAgent,
    create_main_agent,
    MAIN_AGENT_SYSTEM_PROMPT
)
from .analysis_subagent import (
    get_analysis_subagent_config,
    get_analysis_subagent_system_prompt,
    create_analysis_task
)
from .report_subagent import (
    get_report_subagent_config,
    create_report_task,
    get_report_template_structure
)
from .dashboard_subagent import (
    get_dashboard_subagent_config,
    create_dashboard_task,
    get_dashboard_data_format
)

__all__ = [
    # Main Agent
    "MainLegalRiskAnalysisAgent",
    "create_main_agent",
    "MAIN_AGENT_SYSTEM_PROMPT",
    # Analysis Subagent
    "get_analysis_subagent_config",
    "get_analysis_subagent_system_prompt",
    "create_analysis_task",
    # Report Subagent
    "get_report_subagent_config",
    "create_report_task",
    "get_report_template_structure",
    # Dashboard Subagent
    "get_dashboard_subagent_config",
    "create_dashboard_task",
    "get_dashboard_data_format"
]
