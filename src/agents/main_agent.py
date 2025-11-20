"""
Main Legal Risk Analysis Deep Agent

This is the orchestrating agent that coordinates the analysis workflow,
delegates to specialized subagents, and produces final outputs.
"""

from typing import List, Dict, Any, Optional
import json

from ..models.data_room import DataRoom, LegalRiskAnalysisReport


# System prompt for the main Legal Risk Analysis Deep Agent
MAIN_AGENT_SYSTEM_PROMPT = """You are the Legal Risk Analysis Deep Agent, an expert system for comprehensive legal risk assessment of document collections. You orchestrate a team of specialized subagents to analyze legal documents and produce professional risk analysis outputs.

## Your Capabilities

### Skills Available
1. **Legal Risk Analysis Skill**: Systematic approach to identify, categorize, and assess legal risks using the Retrieve → Analyze → Create methodology
2. **Create Legal Risk Analysis Report**: Generate formal Word documents with professional formatting and structure
3. **Legal Risk Analysis Interactive Dashboard**: Create web-based interactive dashboards for risk visualization

### Subagent Team
You can delegate tasks to specialized subagents:

1. **Analysis Subagent**: Performs deep document analysis using Data Room tools and web research
2. **Report Subagent**: Creates formal DOCX reports with proper formatting
3. **Dashboard Subagent**: Builds interactive web dashboards for data visualization

## Workflow Overview

When given a legal risk analysis task, follow this workflow:

### Phase 1: Planning
1. Review the Data Room Index provided in user content
2. Understand the scope and types of documents available
3. Plan the analysis approach based on document types and priorities

### Phase 2: Analysis (Delegate to Analysis Subagent)
Task the Analysis Subagent to:
- Retrieve and analyze documents from the data room
- Identify risks across all categories
- Research relevant legal precedents and regulations
- Generate structured risk findings

### Phase 3: Report Generation (Delegate to Report Subagent)
Task the Report Subagent to:
- Create a formal Legal Risk Analysis Report in Word format
- Include executive summary, detailed findings, and recommendations
- Apply professional formatting and styling

### Phase 4: Dashboard Creation (Delegate to Dashboard Subagent)
Task the Dashboard Subagent to:
- Create an interactive web dashboard
- Visualize risk distribution and categories
- Enable filtering and drill-down capabilities

### Phase 5: Synthesis
- Compile all outputs
- Provide executive briefing to user
- Highlight critical findings and immediate actions needed

## Communication Guidelines

When delegating to subagents:
- Provide clear, specific task descriptions
- Include relevant context from previous phases
- Specify expected output format
- Set priorities and constraints

When reporting to user:
- Lead with critical findings
- Summarize key statistics
- Highlight recommended actions
- Provide access to detailed outputs (report and dashboard)

## Quality Standards

Ensure all outputs meet these standards:
- **Accuracy**: All findings must be supported by document evidence
- **Completeness**: All documents must be analyzed
- **Clarity**: Clear categorization and descriptions
- **Actionability**: Specific, implementable recommendations
- **Professional**: Publication-ready formatting

## Confidentiality

All documents in the data room are confidential. Ensure:
- No external data is mixed with analysis
- Findings are based solely on provided documents
- Outputs are marked as confidential where appropriate
"""


class MainLegalRiskAnalysisAgent:
    """
    Main orchestrating agent for Legal Risk Analysis.

    This agent coordinates the workflow between subagents and manages
    the overall analysis process.
    """

    def __init__(
        self,
        data_room: DataRoom,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the main agent.

        Args:
            data_room: The DataRoom instance to analyze.
            config: Optional configuration dictionary.
        """
        self.data_room = data_room
        self.config = config or {}
        self.analysis_results = None
        self.report_path = None
        self.dashboard_path = None

    def get_system_prompt(self) -> str:
        """Get the system prompt for the main agent."""
        return MAIN_AGENT_SYSTEM_PROMPT

    def get_user_content(self) -> str:
        """
        Generate the user content with Data Room Index.

        Returns:
            Formatted string with document summaries.
        """
        index = self.data_room.get_summary_index()

        content = "## Data Room Index\n\n"
        content += "The following documents are available for analysis:\n\n"

        for i, doc_info in enumerate(index, 1):
            content += f"{i}. {doc_info['summdesc']}\n"

        content += f"\nTotal documents: {len(index)}\n"

        return content

    def get_subagent_configurations(self) -> Dict[str, Dict[str, Any]]:
        """
        Get configurations for all subagents.

        Returns:
            Dictionary of subagent configurations.
        """
        # Get detailed index for subagents
        detailed_index = self.data_room.get_document_index()

        return {
            "analysis": self._get_analysis_subagent_config(detailed_index),
            "report": self._get_report_subagent_config(),
            "dashboard": self._get_dashboard_subagent_config()
        }

    def _get_analysis_subagent_config(
        self,
        data_room_index: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Get configuration for the Analysis Subagent."""
        from .analysis_subagent import get_analysis_subagent_config
        return get_analysis_subagent_config(data_room_index)

    def _get_report_subagent_config(self) -> Dict[str, Any]:
        """Get configuration for the Report Subagent."""
        from .report_subagent import get_report_subagent_config
        return get_report_subagent_config()

    def _get_dashboard_subagent_config(self) -> Dict[str, Any]:
        """Get configuration for the Dashboard Subagent."""
        from .dashboard_subagent import get_dashboard_subagent_config
        return get_dashboard_subagent_config()

    def create_task_for_subagent(
        self,
        subagent_type: str,
        task_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a task definition for a subagent.

        Args:
            subagent_type: Type of subagent (analysis, report, dashboard).
            task_description: Description of the task to perform.
            context: Optional context from previous phases.

        Returns:
            Task definition dictionary.
        """
        configs = self.get_subagent_configurations()

        if subagent_type not in configs:
            raise ValueError(f"Unknown subagent type: {subagent_type}")

        config = configs[subagent_type]

        task = {
            "subagent_name": config["name"],
            "system_prompt": config["system_prompt"],
            "tools": config["tools"],
            "task": task_description
        }

        if context:
            task["context"] = context

        return task

    def process_analysis_results(
        self,
        results: Dict[str, Any]
    ) -> LegalRiskAnalysisReport:
        """
        Process results from the Analysis Subagent.

        Args:
            results: Raw analysis results from subagent.

        Returns:
            Structured LegalRiskAnalysisReport.
        """
        # Convert raw results to structured report
        # This would parse the subagent output and create proper data structures
        self.analysis_results = results
        return results

    def get_final_summary(self) -> Dict[str, Any]:
        """
        Generate final summary of the analysis.

        Returns:
            Summary dictionary with key findings and outputs.
        """
        return {
            "status": "completed",
            "data_room": self.data_room.name,
            "documents_analyzed": len(self.data_room.documents),
            "analysis_results": self.analysis_results,
            "outputs": {
                "report": self.report_path,
                "dashboard": self.dashboard_path
            }
        }


def create_main_agent(
    data_room: DataRoom,
    config: Optional[Dict[str, Any]] = None
) -> MainLegalRiskAnalysisAgent:
    """
    Factory function to create the main agent.

    Args:
        data_room: The DataRoom to analyze.
        config: Optional configuration.

    Returns:
        Configured MainLegalRiskAnalysisAgent instance.
    """
    return MainLegalRiskAnalysisAgent(data_room, config)
