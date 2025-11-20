"""
Configuration for Legal Risk Analysis System

This module contains configuration settings for the agent system,
API integrations, and default parameters.
"""

from typing import Dict, Any, Optional
import os
from dataclasses import dataclass, field


@dataclass
class APIConfig:
    """Configuration for Anthropic API."""
    api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    model: str = "claude-sonnet-4-5-20250929"
    max_tokens: int = 8192
    temperature: float = 0.0

    # Beta headers for advanced features
    beta_headers: list = field(default_factory=lambda: [
        "skills-2025-10-02",
        "files-api-2025-04-14"
    ])


@dataclass
class AgentConfig:
    """Configuration for agent behavior."""
    # Main agent settings
    main_agent_model: str = "claude-sonnet-4-5-20250929"

    # Subagent settings
    analysis_subagent_model: str = "claude-sonnet-4-5-20250929"
    report_subagent_model: str = "claude-sonnet-4-5-20250929"
    dashboard_subagent_model: str = "claude-sonnet-4-5-20250929"

    # Task settings
    max_retries: int = 3
    timeout_seconds: int = 300

    # Analysis settings
    parallel_document_analysis: bool = True
    max_concurrent_analyses: int = 5


@dataclass
class OutputConfig:
    """Configuration for output generation."""
    output_directory: str = "./output"
    report_filename: str = "legal_risk_analysis_report.docx"
    dashboard_filename: str = "legal_risk_analysis_dashboard.html"

    # Report options
    include_methodology: bool = True
    include_appendices: bool = True
    report_organization: str = "by_risk_level"  # or "by_category"

    # Dashboard options
    dashboard_theme: str = "light"
    show_charts: bool = True
    enable_export: bool = True


@dataclass
class WebResearchConfig:
    """Configuration for web research tools."""
    enabled: bool = True
    max_search_results: int = 10
    allowed_domains: list = field(default_factory=list)
    blocked_domains: list = field(default_factory=list)
    rate_limit_requests_per_minute: int = 30


@dataclass
class SystemConfig:
    """Complete system configuration."""
    api: APIConfig = field(default_factory=APIConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    web_research: WebResearchConfig = field(default_factory=WebResearchConfig)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "SystemConfig":
        """Create configuration from dictionary."""
        api_config = APIConfig(**config_dict.get("api", {}))
        agent_config = AgentConfig(**config_dict.get("agent", {}))
        output_config = OutputConfig(**config_dict.get("output", {}))
        web_config = WebResearchConfig(**config_dict.get("web_research", {}))

        return cls(
            api=api_config,
            agent=agent_config,
            output=output_config,
            web_research=web_config
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "api": {
                "api_key": "***",  # Don't expose API key
                "model": self.api.model,
                "max_tokens": self.api.max_tokens,
                "temperature": self.api.temperature
            },
            "agent": {
                "main_agent_model": self.agent.main_agent_model,
                "analysis_subagent_model": self.agent.analysis_subagent_model,
                "report_subagent_model": self.agent.report_subagent_model,
                "dashboard_subagent_model": self.agent.dashboard_subagent_model,
                "max_retries": self.agent.max_retries,
                "timeout_seconds": self.agent.timeout_seconds
            },
            "output": {
                "output_directory": self.output.output_directory,
                "report_filename": self.output.report_filename,
                "dashboard_filename": self.output.dashboard_filename
            },
            "web_research": {
                "enabled": self.web_research.enabled,
                "max_search_results": self.web_research.max_search_results
            }
        }


# Default configuration instance
DEFAULT_CONFIG = SystemConfig()


def get_config(config_path: Optional[str] = None) -> SystemConfig:
    """
    Get system configuration.

    Args:
        config_path: Optional path to configuration file.

    Returns:
        SystemConfig instance.
    """
    if config_path:
        import json
        with open(config_path, 'r') as f:
            config_dict = json.load(f)
        return SystemConfig.from_dict(config_dict)

    return DEFAULT_CONFIG


# Risk level definitions for reference
RISK_LEVELS = {
    "critical": {
        "name": "Critical",
        "color": "#DC3545",
        "priority": 1,
        "description": "Immediate action required; potential for significant legal liability"
    },
    "high": {
        "name": "High",
        "color": "#FD7E14",
        "priority": 2,
        "description": "Prompt attention needed; material risk requiring action within 1-2 weeks"
    },
    "medium": {
        "name": "Medium",
        "color": "#FFC107",
        "priority": 3,
        "description": "Should be addressed within 30 days; moderate exposure"
    },
    "low": {
        "name": "Low",
        "color": "#28A745",
        "priority": 4,
        "description": "Minor issues to address in normal course"
    },
    "informational": {
        "name": "Informational",
        "color": "#17A2B8",
        "priority": 5,
        "description": "For awareness only; no immediate action needed"
    }
}


# Risk categories for analysis
RISK_CATEGORIES = [
    "Contractual",
    "Compliance",
    "Financial",
    "Operational",
    "Litigation",
    "Intellectual Property",
    "Data Privacy",
    "Environmental",
    "Employment",
    "Corporate Governance"
]
