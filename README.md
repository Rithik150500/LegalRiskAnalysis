# Legal Risk Analysis Deep Agent System

A comprehensive system for analyzing legal documents and identifying risks using Claude's Deep Agent architecture with specialized subagents.

## Overview

This system implements a multi-agent architecture for legal risk analysis:

```
┌─────────────────────────────────────────────┐
│     Legal Risk Analysis Deep Agent          │
│  (Orchestrator with Skills & Subagents)     │
└─────────────────┬───────────────────────────┘
                  │
     ┌────────────┼────────────┐
     ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│Analysis │  │ Report  │  │Dashboard│
│Subagent │  │Subagent │  │Subagent │
└─────────┘  └─────────┘  └─────────┘
```

## Architecture

### Data Room Structure

```python
Data Room
├── Documents []
│   ├── doc_id
│   ├── summdesc (summary description)
│   └── Pages []
│       ├── page_num
│       ├── summdesc
│       └── page_image (base64)
```

### Main Deep Agent

The orchestrating agent with access to:
- **Legal Risk Analysis Skill**: Systematic risk identification methodology
- **Create Legal Risk Analysis Report Skill**: DOCX report generation
- **Legal Risk Analysis Interactive Dashboard Skill**: Web dashboard creation

### Subagents

1. **Analysis Subagent**
   - System Prompt: Data Room Index + Legal Risk Analysis Skill (Retrieve → Analyze → Create)
   - Tools: `get_document`, `get_document_pages`, `web_search`, `web_fetch`

2. **Report Subagent**
   - System Prompt: Create Legal Risk Analysis Report Skill + DOCX Skill
   - Output: Professional Word document

3. **Dashboard Subagent**
   - System Prompt: Create Legal Risk Analysis Interactive Dashboard Skill + Web Artifact Builder Skill
   - Output: Interactive HTML dashboard

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd LegalRiskAnalysis

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from src import (
    create_sample_data_room,
    create_main_agent,
    get_config
)

# Create or load data room
data_room = create_sample_data_room()

# Get configuration
config = get_config()

# Create main agent
agent = create_main_agent(data_room, config.to_dict())

# Get system prompt and user content
system_prompt = agent.get_system_prompt()
user_content = agent.get_user_content()

# Get subagent configurations
subagents = agent.get_subagent_configurations()
```

### CLI Usage

```bash
# Run with sample data
python -m src.main --sample --output-dir ./output

# Run with custom data room
python -m src.main --data-room /path/to/data_room.json --output-dir ./output

# Run with custom config
python -m src.main --sample --config /path/to/config.json
```

### Data Room Format

```json
{
  "name": "Project Data Room",
  "description": "Legal documents for analysis",
  "documents": [
    {
      "doc_id": "DOC-001",
      "summdesc": "Summary of the document",
      "document_type": "contract",
      "title": "Service Agreement",
      "pages": [
        {
          "page_num": 1,
          "summdesc": "Summary of page content",
          "page_image": "base64-encoded-image"
        }
      ]
    }
  ]
}
```

## Skills

### Legal Risk Analysis Skill

Located at `.claude/skills/legal-risk-analysis/SKILL.md`

Implements the Retrieve → Analyze → Create methodology:
- **Retrieve**: Systematically gather document content
- **Analyze**: Identify risks across categories (Contractual, Compliance, Financial, Operational, Litigation)
- **Create**: Generate structured risk findings

### DOCX Generation Skill

Located at `.claude/skills/docx-generation/SKILL.md`

Capabilities:
- Professional document structure
- Risk-level color coding
- Tables and formatting
- Executive summaries

### Web Artifact Builder Skill

Located at `.claude/skills/web-artifact-builder/SKILL.md`

Capabilities:
- Interactive charts (Chart.js)
- Filter and search functionality
- Responsive design
- Drill-down details

## Tools

### Data Room Tools

```python
# Get document summary
get_document(doc_id) -> combined summdesc of all pages

# Get specific pages with images
get_document_pages(doc_id, page_nums[]) -> page images and content
```

### Web Research Tools

```python
# Search for legal information
web_search(query, num_results, jurisdiction, date_range)

# Fetch content from URL
web_fetch(url, extract_tables, include_metadata)
```

## Risk Levels

| Level | Color | Description |
|-------|-------|-------------|
| Critical | 🔴 Red | Immediate action required |
| High | 🟠 Orange | Prompt attention needed |
| Medium | 🟡 Yellow | Address within 30 days |
| Low | 🟢 Green | Minor issues |
| Info | 🔵 Blue | For awareness only |

## Risk Categories

- Contractual
- Compliance
- Financial
- Operational
- Litigation
- Intellectual Property
- Data Privacy
- Environmental
- Employment
- Corporate Governance

## Output

### Legal Risk Analysis Report (DOCX)

- Cover page
- Table of contents
- Executive summary
- Risk summary with statistics
- Detailed findings
- Recommendations
- Methodology
- Appendices

### Interactive Dashboard (HTML)

- KPI cards
- Risk distribution charts
- Category breakdown
- Filterable findings list
- Detail modals
- Export functionality

## Project Structure

```
LegalRiskAnalysis/
├── .claude/
│   └── skills/
│       ├── legal-risk-analysis/
│       │   └── SKILL.md
│       ├── docx-generation/
│       │   └── SKILL.md
│       └── web-artifact-builder/
│           └── SKILL.md
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── data_room.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── data_room_tools.py
│   │   └── web_tools.py
│   └── agents/
│       ├── __init__.py
│       ├── main_agent.py
│       ├── analysis_subagent.py
│       ├── report_subagent.py
│       └── dashboard_subagent.py
├── requirements.txt
└── README.md
```

## Configuration

Configuration can be customized via JSON file:

```json
{
  "api": {
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 8192
  },
  "agent": {
    "max_retries": 3,
    "timeout_seconds": 300
  },
  "output": {
    "output_directory": "./output",
    "report_filename": "legal_risk_analysis_report.docx",
    "dashboard_filename": "legal_risk_analysis_dashboard.html"
  },
  "web_research": {
    "enabled": true,
    "max_search_results": 10
  }
}
```

## Integration with Claude API

To use this system with the Claude API:

```python
import anthropic
from src import create_main_agent, create_sample_data_room

# Initialize client
client = anthropic.Anthropic()

# Set up data room and agent
data_room = create_sample_data_room()
agent = create_main_agent(data_room)

# Get configuration
system_prompt = agent.get_system_prompt()
user_content = agent.get_user_content()

# Make API call
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=8192,
    system=system_prompt,
    messages=[
        {"role": "user", "content": user_content}
    ]
)
```

## License

[License information]

## Contributing

[Contribution guidelines]
