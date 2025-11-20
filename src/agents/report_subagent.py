"""
Report Subagent for Legal Risk Analysis

This subagent creates formal Legal Risk Analysis Reports in Word format
using the DOCX generation skill.
"""

from typing import Dict, Any, List


REPORT_SUBAGENT_SYSTEM_PROMPT = """You are the Report Generation Subagent, specialized in creating professional Legal Risk Analysis Reports in Microsoft Word format. You combine legal analysis findings with document formatting expertise to produce publication-ready reports.

## Skills Available

### Create Legal Risk Analysis Report Skill
Generate comprehensive Word documents with:
- Professional formatting and structure
- Risk findings presented clearly
- Visual risk indicators
- Executive summary
- Actionable recommendations

### DOCX Skill
Technical capabilities for Word document creation:
- Document structure with headers and sections
- Formatted tables for data presentation
- Color-coded risk levels
- Table of contents
- Professional styling

## Report Structure

Create reports with this structure:

### 1. Cover Page
- Report title
- Data room name
- Preparation date
- Confidentiality notice

### 2. Table of Contents
- Auto-generated from headings
- Page numbers

### 3. Executive Summary (1-2 pages)
- Overall risk rating
- Key statistics
- Top 5 critical/high findings
- Immediate action items

### 4. Risk Summary
- Summary table with counts by risk level
- Distribution visualization description
- Key themes identified

### 5. Detailed Findings
For each finding:
- Risk ID and Title
- Risk Level (color-coded)
- Category
- Source Document and Pages
- Detailed Description
- Legal Basis
- Potential Impact
- Recommendations

Organize by:
- Risk level (Critical first, then High, etc.)
- Or by category if specified

### 6. Findings by Document
- Summary table per document
- Quick reference for document-specific issues

### 7. Recommendations Summary
Prioritized action list:
- Immediate (Critical/High risks)
- Short-term (Medium risks)
- Ongoing monitoring (Low/Info)

### 8. Methodology
- Analysis approach
- Tools used
- Limitations and assumptions

### 9. Appendices
- Document index
- Glossary
- Legal references

## Formatting Standards

### Risk Level Colors
- Critical: Red (#DC3545)
- High: Orange (#FD7E14)
- Medium: Yellow (#FFC107)
- Low: Green (#28A745)
- Informational: Blue (#17A2B8)

### Typography
- Title: Arial 24pt Bold
- Heading 1: Arial 16pt Bold
- Heading 2: Arial 14pt Bold
- Body: Times New Roman 11pt
- Tables: Calibri 10pt

### Spacing
- Line spacing: 1.15
- Paragraph after: 6pt
- Section spacing: 12pt

### Tables
- Header row: Bold, background color
- Alternating row colors for readability
- Proper column alignment

## Python-docx Code Generation

When asked to generate the report, provide Python code using python-docx:

```python
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def create_legal_risk_report(analysis_data: dict, output_path: str):
    '''Create Legal Risk Analysis Report from analysis data.'''
    doc = Document()

    # Document properties
    doc.core_properties.title = analysis_data.get('title', 'Legal Risk Analysis Report')
    doc.core_properties.author = 'Legal Risk Analysis System'

    # Cover page
    # ... implementation

    # Content sections
    # ... implementation

    doc.save(output_path)
    return output_path
```

## Input Requirements

You will receive:
1. Analysis results with all risk findings
2. Metadata (data room name, date, etc.)
3. Any specific formatting requirements

## Output

Provide:
1. Complete Python code to generate the DOCX
2. The code should be executable with python-docx
3. All styling and formatting included
4. Instructions for running the code

## Quality Checklist

Before finalizing:
- [ ] All findings included
- [ ] Correct risk level colors
- [ ] Tables properly formatted
- [ ] Page breaks appropriate
- [ ] TOC will generate correctly
- [ ] Confidentiality notice included
- [ ] No spelling/grammar errors
- [ ] Professional appearance
"""


def get_report_subagent_config() -> Dict[str, Any]:
    """
    Get the complete configuration for the Report Subagent.

    Returns:
        Configuration dictionary with name, system_prompt, and tools.
    """
    return {
        "name": "report-subagent",
        "description": "Creates formal Legal Risk Analysis Reports in Word format with professional formatting",
        "system_prompt": REPORT_SUBAGENT_SYSTEM_PROMPT,
        "tools": [
            "write_file",
            "read_file"
        ],
        "model": "claude-sonnet-4-5-20250929"
    }


def create_report_task(
    analysis_results: Dict[str, Any],
    output_path: str,
    report_options: Dict[str, Any] = None
) -> str:
    """
    Create a task prompt for the Report Subagent.

    Args:
        analysis_results: Complete analysis results from Analysis Subagent.
        output_path: Path where the report should be saved.
        report_options: Optional report customization options.

    Returns:
        Formatted task prompt.
    """
    import json

    options = report_options or {}

    task = f"""## Report Generation Task

Create a professional Legal Risk Analysis Report in Word format.

### Output Path
{output_path}

### Analysis Data
```json
{json.dumps(analysis_results, indent=2)}
```

### Report Options
- Organization: {options.get('organization', 'By risk level')}
- Include methodology: {options.get('include_methodology', True)}
- Include appendices: {options.get('include_appendices', True)}
- Color scheme: {options.get('color_scheme', 'Standard')}

### Instructions

1. Generate complete Python code using python-docx
2. Include all sections as specified in your system prompt
3. Apply proper formatting and styling
4. Ensure all findings are included with full details
5. The code should be directly executable

Provide the complete Python code to generate this report.
"""

    return task


def get_report_template_structure() -> Dict[str, Any]:
    """
    Get the template structure for the report.

    Returns:
        Dictionary describing report structure.
    """
    return {
        "sections": [
            {
                "name": "cover_page",
                "heading_level": None,
                "required": True
            },
            {
                "name": "table_of_contents",
                "heading_level": None,
                "required": True
            },
            {
                "name": "executive_summary",
                "heading_level": 1,
                "required": True
            },
            {
                "name": "risk_summary",
                "heading_level": 1,
                "required": True
            },
            {
                "name": "detailed_findings",
                "heading_level": 1,
                "required": True
            },
            {
                "name": "findings_by_document",
                "heading_level": 1,
                "required": False
            },
            {
                "name": "recommendations_summary",
                "heading_level": 1,
                "required": True
            },
            {
                "name": "methodology",
                "heading_level": 1,
                "required": False
            },
            {
                "name": "appendices",
                "heading_level": 1,
                "required": False
            }
        ],
        "styles": {
            "title": {"font": "Arial", "size": 24, "bold": True},
            "heading1": {"font": "Arial", "size": 16, "bold": True},
            "heading2": {"font": "Arial", "size": 14, "bold": True},
            "body": {"font": "Times New Roman", "size": 11},
            "table": {"font": "Calibri", "size": 10}
        }
    }
