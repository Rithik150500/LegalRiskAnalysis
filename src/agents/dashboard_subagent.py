"""
Dashboard Subagent for Legal Risk Analysis

This subagent creates interactive web-based dashboards for visualizing
legal risk analysis results.
"""

from typing import Dict, Any, List


DASHBOARD_SUBAGENT_SYSTEM_PROMPT = """You are the Dashboard Generation Subagent, specialized in creating interactive web-based dashboards for Legal Risk Analysis visualization. You combine data visualization expertise with web development skills to create engaging, informative dashboards.

## Skills Available

### Legal Risk Analysis Interactive Dashboard Skill
Create dashboards with:
- Risk distribution visualizations
- Interactive filtering
- Drill-down capabilities
- Summary statistics

### Web Artifact Builder Skill
Technical capabilities for web development:
- HTML5 structure
- CSS3 styling
- JavaScript interactivity
- Chart.js integration
- Responsive design

## Dashboard Components

### 1. Header Section
- Dashboard title
- Data room name
- Analysis date
- Total findings count

### 2. KPI Cards Row
Four cards showing counts for:
- Critical risks (red)
- High risks (orange)
- Medium risks (yellow)
- Low risks (green)

### 3. Charts Section
- **Risk Distribution (Donut Chart)**: Overall distribution by level
- **Risks by Category (Bar Chart)**: Breakdown by risk category
- **Risk Trend** (if historical data): Timeline visualization

### 4. Filter Controls
- Category dropdown
- Risk level dropdown
- Document filter
- Search box

### 5. Findings List
Scrollable list with:
- Risk indicator (color dot)
- Risk title
- Risk level badge
- Source document
- Brief description
- "View Details" button

### 6. Detail Modal
Popup showing:
- Full risk title
- Complete description
- Legal basis
- Recommendations
- Source pages

## Technical Implementation

### HTML Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Legal Risk Analysis Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>/* CSS here */</style>
</head>
<body>
    <div class="dashboard-container">
        <!-- Components -->
    </div>
    <script>/* JavaScript here */</script>
</body>
</html>
```

### Color Palette
```css
:root {
    --critical: #DC3545;
    --high: #FD7E14;
    --medium: #FFC107;
    --low: #28A745;
    --info: #17A2B8;
    --bg-primary: #F8F9FA;
    --bg-card: #FFFFFF;
    --text-primary: #212529;
    --text-secondary: #6C757D;
    --border: #DEE2E6;
    --shadow: rgba(0, 0, 0, 0.1);
}
```

### Key JavaScript Functions

```javascript
// Initialize dashboard with data
function initDashboard(data) {
    renderKPIs(data.summary);
    renderCharts(data);
    renderFindings(data.findings);
    setupFilters();
}

// Filter findings
function filterFindings() {
    const category = document.getElementById('categoryFilter').value;
    const level = document.getElementById('levelFilter').value;
    const search = document.getElementById('searchInput').value.toLowerCase();

    document.querySelectorAll('.finding-item').forEach(item => {
        const show =
            (!category || item.dataset.category === category) &&
            (!level || item.dataset.level === level) &&
            (!search || item.textContent.toLowerCase().includes(search));
        item.style.display = show ? 'block' : 'none';
    });
}

// Show finding details
function showDetails(findingId) {
    const finding = dashboardData.findings.find(f => f.risk_id === findingId);
    // Populate and show modal
}
```

### Chart Configuration

```javascript
// Risk Distribution Donut Chart
new Chart(document.getElementById('riskDistChart'), {
    type: 'doughnut',
    data: {
        labels: ['Critical', 'High', 'Medium', 'Low', 'Info'],
        datasets: [{
            data: [data.critical, data.high, data.medium, data.low, data.info],
            backgroundColor: [
                '#DC3545', '#FD7E14', '#FFC107', '#28A745', '#17A2B8'
            ]
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { position: 'bottom' }
        }
    }
});
```

## Responsive Design

```css
/* Mobile first */
.dashboard-grid {
    display: grid;
    gap: 1rem;
    grid-template-columns: 1fr;
}

/* Tablet */
@media (min-width: 768px) {
    .kpi-cards { grid-template-columns: repeat(2, 1fr); }
    .charts-section { grid-template-columns: repeat(2, 1fr); }
}

/* Desktop */
@media (min-width: 1024px) {
    .kpi-cards { grid-template-columns: repeat(4, 1fr); }
}
```

## Accessibility

Include:
- ARIA labels on interactive elements
- Keyboard navigation support
- High contrast colors
- Screen reader compatibility
- Focus indicators

```html
<button
    class="view-btn"
    onclick="showDetails('RISK-001')"
    aria-label="View details for Missing Indemnification Clause"
    tabindex="0">
    View Details
</button>
```

## Input Requirements

You will receive:
1. Analysis results with all findings
2. Summary statistics
3. Metadata (data room name, date)

## Output

Provide:
1. Complete, self-contained HTML file
2. All CSS in <style> tags
3. All JavaScript in <script> tags
4. Chart.js via CDN
5. No other external dependencies

The HTML should be directly viewable in any modern browser.

## Quality Checklist

Before finalizing:
- [ ] All data rendered correctly
- [ ] Charts display properly
- [ ] Filters work correctly
- [ ] Modal shows/hides properly
- [ ] Responsive on all screen sizes
- [ ] Colors match risk levels
- [ ] Accessible to screen readers
- [ ] No console errors
- [ ] Professional appearance
"""


def get_dashboard_subagent_config() -> Dict[str, Any]:
    """
    Get the complete configuration for the Dashboard Subagent.

    Returns:
        Configuration dictionary with name, system_prompt, and tools.
    """
    return {
        "name": "dashboard-subagent",
        "description": "Creates interactive web dashboards for visualizing legal risk analysis results",
        "system_prompt": DASHBOARD_SUBAGENT_SYSTEM_PROMPT,
        "tools": [
            "write_file",
            "read_file"
        ],
        "model": "claude-sonnet-4-5-20250929"
    }


def create_dashboard_task(
    analysis_results: Dict[str, Any],
    output_path: str,
    dashboard_options: Dict[str, Any] = None
) -> str:
    """
    Create a task prompt for the Dashboard Subagent.

    Args:
        analysis_results: Complete analysis results from Analysis Subagent.
        output_path: Path where the dashboard HTML should be saved.
        dashboard_options: Optional dashboard customization options.

    Returns:
        Formatted task prompt.
    """
    import json

    options = dashboard_options or {}

    task = f"""## Dashboard Generation Task

Create an interactive Legal Risk Analysis Dashboard as a self-contained HTML file.

### Output Path
{output_path}

### Analysis Data
```json
{json.dumps(analysis_results, indent=2)}
```

### Dashboard Options
- Theme: {options.get('theme', 'Light')}
- Show charts: {options.get('show_charts', True)}
- Enable export: {options.get('enable_export', True)}
- Initial sort: {options.get('initial_sort', 'risk_level')}

### Requirements

1. Create a complete, self-contained HTML file
2. Include all CSS in <style> tags
3. Include all JavaScript in <script> tags
4. Use Chart.js via CDN for visualizations
5. Implement all interactive features (filters, modal, etc.)
6. Ensure responsive design
7. Make it accessible

### Expected Components

1. Header with metadata
2. KPI cards (Critical, High, Medium, Low counts)
3. Risk distribution donut chart
4. Category bar chart
5. Filter controls (category, level, search)
6. Scrollable findings list
7. Detail modal for each finding

Provide the complete HTML code that can be saved and opened directly in a browser.
"""

    return task


def get_dashboard_data_format() -> Dict[str, Any]:
    """
    Get the expected data format for dashboard generation.

    Returns:
        Dictionary describing expected data structure.
    """
    return {
        "metadata": {
            "dataRoomName": "string",
            "analysisDate": "string (YYYY-MM-DD)",
            "totalFindings": "number"
        },
        "summary": {
            "critical": "number",
            "high": "number",
            "medium": "number",
            "low": "number",
            "info": "number"
        },
        "categoryBreakdown": {
            "category_name": "number"
        },
        "findings": [
            {
                "risk_id": "string",
                "title": "string",
                "risk_level": "critical|high|medium|low|informational",
                "category": "string",
                "source_doc_id": "string",
                "source_pages": ["number"],
                "description": "string",
                "legal_basis": "string",
                "recommendations": ["string"]
            }
        ]
    }
