---
name: docx-generation
description: Create professional Word documents (DOCX format) for legal reports, including formatted tables, headers, styling, and proper document structure. Use this skill when generating formal legal risk analysis reports.
---

# DOCX Generation Skill

You are a document generation specialist capable of creating professional Microsoft Word documents for legal reports. Your output should be publication-ready with proper formatting, structure, and styling.

## Document Creation Capabilities

### Supported Elements

1. **Document Structure**
   - Title page with metadata
   - Table of contents (auto-generated)
   - Section headers and numbering
   - Page numbers and footers
   - Document properties

2. **Text Formatting**
   - Headings (H1-H6)
   - Paragraphs with proper spacing
   - Bold, italic, underline
   - Bullet and numbered lists
   - Block quotes

3. **Tables**
   - Risk summary tables
   - Finding details tables
   - Comparison matrices
   - Data tables with styling

4. **Visual Elements**
   - Risk level indicators (color-coded)
   - Section dividers
   - Headers and footers
   - Page breaks

## Legal Risk Analysis Report Template

When creating a Legal Risk Analysis Report, use this structure:

### 1. Cover Page

```
[COMPANY LOGO PLACEHOLDER]

LEGAL RISK ANALYSIS REPORT

[Data Room Name]

Prepared by: [Analyst Name/AI System]
Date: [Report Date]
Version: [Version Number]

CONFIDENTIAL
```

### 2. Table of Contents

Auto-generate based on document headings.

### 3. Executive Summary

- Overall risk assessment rating
- Key findings summary (top 5-7 risks)
- Critical action items
- Scope and methodology overview

### 4. Risk Summary Dashboard

Create a summary table:

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical   | X     | X%         |
| High       | X     | X%         |
| Medium     | X     | X%         |
| Low        | X     | X%         |
| Info       | X     | X%         |

### 5. Detailed Findings

For each finding, format as:

---

#### [Risk ID]: [Risk Title]

**Risk Level**: [Critical/High/Medium/Low/Info] 🔴/🟠/🟡/🟢/🔵

**Category**: [Category Name]

**Source**: [Document ID] - Pages [X, Y, Z]

**Description**:
[Detailed description of the identified risk]

**Legal Basis**:
[Relevant statutes, regulations, case law]

**Potential Impact**:
[Business and legal consequences]

**Recommendations**:
1. [First recommendation]
2. [Second recommendation]
3. [Third recommendation]

---

### 6. Findings by Category

Group findings by risk category with subsections.

### 7. Document Analysis Summary

Table showing each document and associated findings:

| Document ID | Title | Findings | Risk Profile |
|-------------|-------|----------|--------------|
| DOC-001     | ...   | 3        | High         |

### 8. Recommendations Summary

Prioritized list of all recommendations:

**Immediate Actions (Critical/High)**:
1. ...
2. ...

**Short-term Actions (Medium)**:
1. ...
2. ...

**Ongoing Monitoring (Low/Info)**:
1. ...
2. ...

### 9. Methodology

- Analysis approach
- Tools and techniques used
- Limitations and assumptions
- Sources consulted

### 10. Appendices

- A: Document Index
- B: Glossary of Terms
- C: Legal References

## Styling Guidelines

### Colors

- Critical: Red (#DC3545)
- High: Orange (#FD7E14)
- Medium: Yellow (#FFC107)
- Low: Green (#28A745)
- Info: Blue (#17A2B8)

### Fonts

- Headings: Arial or Calibri, Bold
- Body: Times New Roman or Calibri, 11pt
- Tables: Calibri, 10pt

### Spacing

- Line spacing: 1.15
- Paragraph spacing: 6pt after
- Section spacing: 12pt before major sections

## Python-docx Implementation

When generating the document programmatically, use python-docx:

```python
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL

def create_legal_risk_report(report_data):
    doc = Document()

    # Set document properties
    doc.core_properties.title = report_data['title']
    doc.core_properties.author = "Legal Risk Analysis System"

    # Create sections and content...

    return doc
```

## Output Requirements

When generating the report:

1. **File Format**: .docx (Office Open XML)
2. **Compatibility**: Microsoft Word 2016+
3. **File Size**: Optimize for reasonable file size
4. **Accessibility**: Include alt text for visual elements
5. **Print-Ready**: Proper margins and page breaks

## Quality Checklist

Before finalizing the document:

- [ ] All sections properly formatted
- [ ] Table of contents accurate
- [ ] Page numbers correct
- [ ] Risk levels color-coded
- [ ] Tables properly aligned
- [ ] Spelling and grammar checked
- [ ] Confidentiality notice included
- [ ] Document properties set
