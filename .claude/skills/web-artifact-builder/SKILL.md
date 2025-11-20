---
name: web-artifact-builder
description: Create interactive web-based dashboards and visualizations for data presentation. Use this skill when building legal risk analysis dashboards with charts, filters, and interactive elements.
---

# Web Artifact Builder Skill

You are a web development specialist capable of creating interactive dashboards and data visualizations. Your output should be self-contained HTML/CSS/JavaScript applications that can be viewed in any modern browser.

## Dashboard Capabilities

### Visualization Types

1. **Charts**
   - Bar charts (risk distribution)
   - Pie/Donut charts (category breakdown)
   - Heat maps (risk matrices)
   - Timeline charts (temporal analysis)
   - Gauge charts (overall risk score)

2. **Tables**
   - Sortable data tables
   - Filterable lists
   - Expandable rows
   - Paginated results

3. **Interactive Elements**
   - Filter controls
   - Search functionality
   - Drill-down navigation
   - Tooltips and popovers
   - Collapsible sections

4. **Summary Cards**
   - KPI cards
   - Risk counters
   - Status indicators
   - Trend indicators

## Legal Risk Analysis Dashboard Template

### Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│  LEGAL RISK ANALYSIS DASHBOARD                    [?]   │
├─────────────────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │Critical │ │  High   │ │ Medium  │ │   Low   │       │
│  │   X     │ │    X    │ │    X    │ │    X    │       │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │  Risk by Category │  │ Risk Distribution │            │
│  │  [Bar Chart]     │  │  [Donut Chart]   │            │
│  └──────────────────┘  └──────────────────┘            │
├─────────────────────────────────────────────────────────┤
│  FILTERS: [Category ▼] [Risk Level ▼] [Document ▼]     │
├─────────────────────────────────────────────────────────┤
│  FINDINGS LIST                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ [●] Risk Title                    High  DOC-001 │   │
│  │     Brief description...              [View →]  │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ [●] Risk Title                  Medium  DOC-002 │   │
│  │     Brief description...              [View →]  │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Component Specifications

#### 1. Header Section

```html
<header class="dashboard-header">
  <h1>Legal Risk Analysis Dashboard</h1>
  <div class="header-meta">
    <span>Data Room: [Name]</span>
    <span>Analysis Date: [Date]</span>
    <span>Total Findings: [Count]</span>
  </div>
</header>
```

#### 2. KPI Cards

```html
<div class="kpi-cards">
  <div class="kpi-card critical">
    <span class="count">5</span>
    <span class="label">Critical</span>
  </div>
  <!-- Repeat for each risk level -->
</div>
```

#### 3. Charts Section

Use Chart.js or similar library:

```javascript
// Risk Distribution Chart
const riskChart = new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: ['Critical', 'High', 'Medium', 'Low', 'Info'],
    datasets: [{
      data: [5, 12, 23, 8, 3],
      backgroundColor: [
        '#DC3545', '#FD7E14', '#FFC107', '#28A745', '#17A2B8'
      ]
    }]
  }
});
```

#### 4. Filter Controls

```html
<div class="filters">
  <select id="categoryFilter">
    <option value="">All Categories</option>
    <option value="contractual">Contractual</option>
    <option value="compliance">Compliance</option>
    <!-- ... -->
  </select>

  <select id="riskLevelFilter">
    <option value="">All Levels</option>
    <option value="critical">Critical</option>
    <!-- ... -->
  </select>

  <input type="search" id="searchInput" placeholder="Search findings...">
</div>
```

#### 5. Findings List

```html
<div class="findings-list">
  <div class="finding-item" data-risk-level="high" data-category="contractual">
    <div class="finding-header">
      <span class="risk-indicator high"></span>
      <h3>Missing Indemnification Clause</h3>
      <span class="risk-badge high">High</span>
    </div>
    <p class="finding-description">
      Contract lacks standard indemnification provisions...
    </p>
    <div class="finding-meta">
      <span>Source: DOC-001</span>
      <span>Category: Contractual</span>
      <button class="view-details">View Details</button>
    </div>
  </div>
</div>
```

#### 6. Detail Modal

```html
<div class="modal" id="findingModal">
  <div class="modal-content">
    <h2 id="modalTitle"></h2>
    <div class="modal-body">
      <div class="detail-section">
        <h4>Description</h4>
        <p id="modalDescription"></p>
      </div>
      <div class="detail-section">
        <h4>Legal Basis</h4>
        <p id="modalLegalBasis"></p>
      </div>
      <div class="detail-section">
        <h4>Recommendations</h4>
        <ul id="modalRecommendations"></ul>
      </div>
    </div>
    <button class="close-modal">Close</button>
  </div>
</div>
```

## Styling Guidelines

### Color Palette

```css
:root {
  /* Risk Level Colors */
  --critical: #DC3545;
  --high: #FD7E14;
  --medium: #FFC107;
  --low: #28A745;
  --info: #17A2B8;

  /* UI Colors */
  --background: #F8F9FA;
  --card-bg: #FFFFFF;
  --text-primary: #212529;
  --text-secondary: #6C757D;
  --border: #DEE2E6;
}
```

### Responsive Design

```css
/* Mobile-first approach */
.kpi-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

@media (min-width: 768px) {
  .kpi-cards {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (min-width: 1024px) {
  .dashboard-layout {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2rem;
  }
}
```

## JavaScript Functionality

### Data Structure

```javascript
const dashboardData = {
  metadata: {
    dataRoomName: "Project Alpha",
    analysisDate: "2025-11-20",
    totalFindings: 51
  },
  summary: {
    critical: 5,
    high: 12,
    medium: 23,
    low: 8,
    info: 3
  },
  findings: [
    {
      id: "RISK-001",
      title: "Missing Indemnification Clause",
      riskLevel: "high",
      category: "contractual",
      sourceDoc: "DOC-001",
      sourcePages: [3, 4, 5],
      description: "...",
      legalBasis: "...",
      recommendations: ["...", "..."]
    }
    // ... more findings
  ]
};
```

### Filter Implementation

```javascript
function filterFindings() {
  const category = document.getElementById('categoryFilter').value;
  const riskLevel = document.getElementById('riskLevelFilter').value;
  const search = document.getElementById('searchInput').value.toLowerCase();

  const findings = document.querySelectorAll('.finding-item');

  findings.forEach(finding => {
    const matchCategory = !category || finding.dataset.category === category;
    const matchLevel = !riskLevel || finding.dataset.riskLevel === riskLevel;
    const matchSearch = !search ||
      finding.textContent.toLowerCase().includes(search);

    finding.style.display =
      matchCategory && matchLevel && matchSearch ? 'block' : 'none';
  });

  updateCounts();
}
```

## Output Requirements

### Self-Contained HTML

Generate a single HTML file that includes:

1. **All CSS** in a `<style>` tag
2. **All JavaScript** in a `<script>` tag
3. **Chart.js** via CDN link
4. **No external dependencies** except CDN libraries

### Browser Compatibility

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

### Performance

- Minimize DOM manipulations
- Use efficient selectors
- Lazy load heavy content
- Optimize chart rendering

## Accessibility

Include:

- ARIA labels
- Keyboard navigation
- Color contrast compliance
- Screen reader support
- Focus indicators

```html
<button
  class="view-details"
  aria-label="View details for risk RISK-001"
  tabindex="0">
  View Details
</button>
```

## Export Options

Include functionality to:

- Print dashboard
- Export data as CSV
- Share dashboard link (if hosted)
- Screenshot/PDF generation

```javascript
function exportToCSV() {
  const csv = findings.map(f =>
    `${f.id},${f.title},${f.riskLevel},${f.category}`
  ).join('\n');

  downloadFile('findings.csv', csv);
}
```
