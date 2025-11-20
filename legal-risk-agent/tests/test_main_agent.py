# test_main_agent.py - Tests for main agent configuration and creation
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock external dependencies before importing main_agent
mock_deepagents = MagicMock()
mock_deepagents.create_deep_agent = MagicMock()
sys.modules['deepagents'] = mock_deepagents

from main_agent import MAIN_AGENT_SYSTEM_PROMPT, create_legal_risk_analysis_agent
from data_room_tools import DataRoom


class TestMainAgentSystemPrompt:
    """Test main agent system prompt"""

    def test_system_prompt_not_empty(self):
        """Test system prompt is not empty"""
        assert len(MAIN_AGENT_SYSTEM_PROMPT) > 0

    def test_system_prompt_defines_role(self):
        """Test system prompt defines coordinator role"""
        prompt = MAIN_AGENT_SYSTEM_PROMPT

        assert "coordinator" in prompt.lower()
        assert "orchestrat" in prompt.lower()

    def test_system_prompt_mentions_subagents(self):
        """Test system prompt mentions subagents"""
        prompt = MAIN_AGENT_SYSTEM_PROMPT

        assert "subagent" in prompt.lower()
        assert "legal-risk-analyzer" in prompt or "analysis" in prompt.lower()
        assert "report-creator" in prompt or "report" in prompt.lower()
        assert "dashboard-creator" in prompt or "dashboard" in prompt.lower()

    def test_system_prompt_defines_workflow_phases(self):
        """Test system prompt defines workflow phases"""
        prompt = MAIN_AGENT_SYSTEM_PROMPT

        assert "phase" in prompt.lower()
        assert "planning" in prompt.lower()
        assert "delegat" in prompt.lower()
        assert "integration" in prompt.lower() or "integrat" in prompt.lower()

    def test_system_prompt_mentions_risk_categories(self):
        """Test system prompt mentions all risk categories"""
        prompt = MAIN_AGENT_SYSTEM_PROMPT

        categories = ["Contractual", "Regulatory", "Litigation", "IP", "Operational"]
        for category in categories:
            assert category in prompt

    def test_system_prompt_defines_tools(self):
        """Test system prompt defines available tools"""
        prompt = MAIN_AGENT_SYSTEM_PROMPT

        assert "write_todos" in prompt
        assert "write_file" in prompt or "file" in prompt.lower()
        assert "task" in prompt.lower()

    def test_system_prompt_emphasizes_quality(self):
        """Test system prompt emphasizes quality over speed"""
        prompt = MAIN_AGENT_SYSTEM_PROMPT

        assert "quality" in prompt.lower()

    def test_system_prompt_provides_examples(self):
        """Test system prompt provides examples"""
        prompt = MAIN_AGENT_SYSTEM_PROMPT

        assert "example" in prompt.lower()

    def test_system_prompt_mentions_parallel_execution(self):
        """Test system prompt mentions parallel execution"""
        prompt = MAIN_AGENT_SYSTEM_PROMPT

        assert "parallel" in prompt.lower()


class TestCreateLegalRiskAnalysisAgent:
    """Test create_legal_risk_analysis_agent function"""

    @pytest.fixture
    def sample_data_room(self):
        """Create sample DataRoom for testing"""
        docs = [
            {
                "doc_id": "DOC001",
                "summdesc": "Test contract",
                "pages": [
                    {"page_num": 1, "summdesc": "Page 1", "page_image": "img1"}
                ]
            }
        ]
        return DataRoom(docs)

    @patch('main_agent.create_deep_agent')
    def test_agent_creation_calls_create_deep_agent(self, mock_create, sample_data_room):
        """Test agent creation calls create_deep_agent"""
        mock_create.return_value = MagicMock()

        agent = create_legal_risk_analysis_agent(
            sample_data_room,
            "test_tavily_key"
        )

        mock_create.assert_called_once()

    @patch('main_agent.create_deep_agent')
    def test_agent_creation_passes_system_prompt(self, mock_create, sample_data_room):
        """Test agent creation passes correct system prompt"""
        mock_create.return_value = MagicMock()

        create_legal_risk_analysis_agent(
            sample_data_room,
            "test_tavily_key"
        )

        call_kwargs = mock_create.call_args[1]
        assert "system_prompt" in call_kwargs
        assert call_kwargs["system_prompt"] == MAIN_AGENT_SYSTEM_PROMPT

    @patch('main_agent.create_deep_agent')
    def test_agent_creation_specifies_model(self, mock_create, sample_data_room):
        """Test agent creation specifies model"""
        mock_create.return_value = MagicMock()

        create_legal_risk_analysis_agent(
            sample_data_room,
            "test_tavily_key"
        )

        call_kwargs = mock_create.call_args[1]
        assert "model" in call_kwargs
        assert "claude" in call_kwargs["model"].lower()

    @patch('main_agent.create_deep_agent')
    def test_agent_creation_includes_subagents(self, mock_create, sample_data_room):
        """Test agent creation includes subagents"""
        mock_create.return_value = MagicMock()

        create_legal_risk_analysis_agent(
            sample_data_room,
            "test_tavily_key"
        )

        call_kwargs = mock_create.call_args[1]
        assert "subagents" in call_kwargs
        assert len(call_kwargs["subagents"]) == 3

    @patch('main_agent.create_deep_agent')
    def test_agent_creation_configures_analysis_subagent_tools(self, mock_create, sample_data_room):
        """Test agent creation configures analysis subagent with tools"""
        mock_create.return_value = MagicMock()

        create_legal_risk_analysis_agent(
            sample_data_room,
            "test_tavily_key"
        )

        call_kwargs = mock_create.call_args[1]
        subagents = call_kwargs["subagents"]

        # Find analysis subagent
        analysis_subagent = None
        for sa in subagents:
            if sa["name"] == "legal-risk-analyzer":
                analysis_subagent = sa
                break

        assert analysis_subagent is not None
        assert "tools" in analysis_subagent
        assert len(analysis_subagent["tools"]) == 4  # get_document, get_document_pages, internet_search, web_fetch

    @patch('main_agent.create_deep_agent')
    def test_agent_returns_created_agent(self, mock_create, sample_data_room):
        """Test function returns the created agent"""
        mock_agent = MagicMock()
        mock_create.return_value = mock_agent

        result = create_legal_risk_analysis_agent(
            sample_data_room,
            "test_tavily_key"
        )

        assert result == mock_agent


class TestAgentIntegration:
    """Test agent configuration integration"""

    @pytest.fixture
    def sample_data_room(self):
        """Create sample DataRoom for testing"""
        docs = [
            {
                "doc_id": "DOC001",
                "summdesc": "Test contract",
                "pages": [
                    {"page_num": 1, "summdesc": "Page 1", "page_image": "img1"}
                ]
            }
        ]
        return DataRoom(docs)

    @patch('main_agent.create_deep_agent')
    @patch('main_agent.create_web_research_tools')
    def test_web_research_tools_are_created(self, mock_web_tools, mock_create, sample_data_room):
        """Test web research tools are created with API key"""
        mock_web_tools.return_value = (MagicMock(), MagicMock())
        mock_create.return_value = MagicMock()

        create_legal_risk_analysis_agent(
            sample_data_room,
            "test_api_key"
        )

        mock_web_tools.assert_called_once_with("test_api_key")

    @patch('main_agent.create_deep_agent')
    @patch('main_agent.create_data_room_tools')
    def test_data_room_tools_are_created(self, mock_dr_tools, mock_create, sample_data_room):
        """Test data room tools are created with data room"""
        mock_dr_tools.return_value = (MagicMock(), MagicMock())
        mock_create.return_value = MagicMock()

        create_legal_risk_analysis_agent(
            sample_data_room,
            "test_api_key"
        )

        mock_dr_tools.assert_called_once_with(sample_data_room)
