# test_subagent_configs.py - Tests for subagent configurations
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis_subagent import ANALYSIS_SUBAGENT_CONFIG, ANALYSIS_SUBAGENT_SYSTEM_PROMPT
from report_subagent import REPORT_SUBAGENT_CONFIG, REPORT_CREATION_SYSTEM_PROMPT


class TestAnalysisSubagentConfig:
    """Test Analysis Subagent configuration"""

    def test_config_has_required_fields(self):
        """Test config has all required fields"""
        assert "name" in ANALYSIS_SUBAGENT_CONFIG
        assert "description" in ANALYSIS_SUBAGENT_CONFIG
        assert "system_prompt" in ANALYSIS_SUBAGENT_CONFIG
        assert "tools" in ANALYSIS_SUBAGENT_CONFIG
        assert "model" in ANALYSIS_SUBAGENT_CONFIG

    def test_config_name(self):
        """Test config has correct name"""
        assert ANALYSIS_SUBAGENT_CONFIG["name"] == "legal-risk-analyzer"

    def test_config_model(self):
        """Test config specifies valid model"""
        model = ANALYSIS_SUBAGENT_CONFIG["model"]
        assert "claude" in model.lower()

    def test_config_tools_is_list(self):
        """Test tools is a list"""
        assert isinstance(ANALYSIS_SUBAGENT_CONFIG["tools"], list)

    def test_system_prompt_not_empty(self):
        """Test system prompt is not empty"""
        assert len(ANALYSIS_SUBAGENT_SYSTEM_PROMPT) > 0

    def test_system_prompt_contains_key_instructions(self):
        """Test system prompt contains key instructions"""
        prompt = ANALYSIS_SUBAGENT_SYSTEM_PROMPT

        # Should contain analytical methodology
        assert "methodology" in prompt.lower() or "approach" in prompt.lower()

        # Should mention risk categories
        assert "contractual" in prompt.lower()
        assert "regulatory" in prompt.lower()
        assert "litigation" in prompt.lower()

        # Should mention severity levels
        assert "critical" in prompt.lower()
        assert "high" in prompt.lower()
        assert "medium" in prompt.lower()
        assert "low" in prompt.lower()

    def test_system_prompt_mentions_tools(self):
        """Test system prompt mentions available tools"""
        prompt = ANALYSIS_SUBAGENT_SYSTEM_PROMPT

        assert "get_document" in prompt
        assert "internet_search" in prompt or "web" in prompt.lower()

    def test_system_prompt_defines_output_format(self):
        """Test system prompt defines output format"""
        prompt = ANALYSIS_SUBAGENT_SYSTEM_PROMPT

        # Should define JSON output format
        assert "json" in prompt.lower()
        assert "risk_id" in prompt
        assert "severity" in prompt
        assert "evidence" in prompt


class TestReportSubagentConfig:
    """Test Report Subagent configuration"""

    def test_config_has_required_fields(self):
        """Test config has all required fields"""
        assert "name" in REPORT_SUBAGENT_CONFIG
        assert "description" in REPORT_SUBAGENT_CONFIG
        assert "system_prompt" in REPORT_SUBAGENT_CONFIG
        assert "tools" in REPORT_SUBAGENT_CONFIG
        assert "model" in REPORT_SUBAGENT_CONFIG

    def test_config_name(self):
        """Test config has correct name"""
        assert REPORT_SUBAGENT_CONFIG["name"] == "report-creator"

    def test_config_model(self):
        """Test config specifies valid model"""
        model = REPORT_SUBAGENT_CONFIG["model"]
        assert "claude" in model.lower()

    def test_system_prompt_not_empty(self):
        """Test system prompt is not empty"""
        assert len(REPORT_CREATION_SYSTEM_PROMPT) > 0

    def test_system_prompt_defines_report_structure(self):
        """Test system prompt defines report structure"""
        prompt = REPORT_CREATION_SYSTEM_PROMPT

        # Should define major sections
        assert "executive summary" in prompt.lower()
        assert "methodology" in prompt.lower()
        assert "recommendation" in prompt.lower()
        assert "appendix" in prompt.lower() or "appendices" in prompt.lower()

    def test_system_prompt_mentions_formatting(self):
        """Test system prompt mentions formatting requirements"""
        prompt = REPORT_CREATION_SYSTEM_PROMPT

        # Should mention document formatting
        assert "format" in prompt.lower()
        assert ".docx" in prompt or "word" in prompt.lower()

    def test_system_prompt_output_location(self):
        """Test system prompt specifies output location"""
        prompt = REPORT_CREATION_SYSTEM_PROMPT

        assert "/outputs/" in prompt or "output" in prompt.lower()


class TestSubagentConfigIntegrity:
    """Test integrity and consistency of subagent configurations"""

    def test_all_configs_have_same_structure(self):
        """Test all configs have consistent structure"""
        configs = [ANALYSIS_SUBAGENT_CONFIG, REPORT_SUBAGENT_CONFIG]
        required_keys = {"name", "description", "system_prompt", "tools", "model"}

        for config in configs:
            config_keys = set(config.keys())
            assert required_keys.issubset(config_keys)

    def test_all_descriptions_are_informative(self):
        """Test all descriptions are informative enough"""
        configs = [ANALYSIS_SUBAGENT_CONFIG, REPORT_SUBAGENT_CONFIG]

        for config in configs:
            # Description should be at least 50 characters
            assert len(config["description"]) >= 50

    def test_all_names_are_unique(self):
        """Test all subagent names are unique"""
        configs = [ANALYSIS_SUBAGENT_CONFIG, REPORT_SUBAGENT_CONFIG]
        names = [config["name"] for config in configs]

        assert len(names) == len(set(names))

    def test_all_prompts_contain_quality_guidelines(self):
        """Test all prompts contain quality guidelines"""
        prompts = [ANALYSIS_SUBAGENT_SYSTEM_PROMPT, REPORT_CREATION_SYSTEM_PROMPT]

        for prompt in prompts:
            # Should mention quality in some form
            has_quality = (
                "quality" in prompt.lower() or
                "accuracy" in prompt.lower() or
                "thorough" in prompt.lower()
            )
            assert has_quality


class TestRiskOutputStructure:
    """Test that the defined risk output structure is complete"""

    def test_analysis_prompt_defines_risk_structure(self):
        """Test analysis prompt defines complete risk structure"""
        prompt = ANALYSIS_SUBAGENT_SYSTEM_PROMPT

        # Required risk fields
        required_fields = [
            "risk_id",
            "category",
            "title",
            "description",
            "severity",
            "likelihood",
            "evidence"
        ]

        for field in required_fields:
            assert field in prompt

    def test_analysis_prompt_defines_evidence_structure(self):
        """Test analysis prompt defines evidence structure"""
        prompt = ANALYSIS_SUBAGENT_SYSTEM_PROMPT

        assert "doc_id" in prompt
        assert "page_num" in prompt
        assert "citation" in prompt

    def test_risk_categories_are_defined(self):
        """Test all risk categories are mentioned"""
        prompt = ANALYSIS_SUBAGENT_SYSTEM_PROMPT

        categories = ["Contractual", "Regulatory", "Litigation", "IP", "Operational"]
        for category in categories:
            assert category in prompt

    def test_severity_levels_are_defined(self):
        """Test all severity levels are mentioned"""
        prompt = ANALYSIS_SUBAGENT_SYSTEM_PROMPT

        levels = ["Critical", "High", "Medium", "Low"]
        for level in levels:
            assert level in prompt

    def test_likelihood_levels_are_defined(self):
        """Test all likelihood levels are mentioned"""
        prompt = ANALYSIS_SUBAGENT_SYSTEM_PROMPT

        levels = ["Very Likely", "Likely", "Possible", "Unlikely"]
        for level in levels:
            assert level in prompt
