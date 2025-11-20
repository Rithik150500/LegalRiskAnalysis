# services/dashboard_generator.py - Interactive HTML Dashboard Generator
import os
import json
from datetime import datetime
from typing import List, Dict, Any


class DashboardGenerator:
    """Generate interactive HTML dashboards for legal risk analysis"""

    def generate_dashboard(
        self,
        analysis_id: str,
        analysis_name: str,
        analysis_summary: str,
        documents: List[Dict],
        risks: List[Dict],
        output_path: str
    ) -> str:
        """
        Generate a complete interactive HTML dashboard

        Args:
            analysis_id: Unique analysis identifier
            analysis_name: Name of the analysis
            analysis_summary: Executive summary text
            documents: List of analyzed documents
            risks: List of identified risks
            output_path: Path to save the dashboard

        Returns:
            Path to the generated dashboard
        """
        # Prepare data for embedding
        dashboard_data = {
            "analysis_id": analysis_id,
            "analysis_name": analysis_name,
            "analysis_summary": analysis_summary,
            "analysis_date": datetime.now().isoformat(),
            "documents": [
                {
                    "doc_id": doc.get("doc_id", ""),
                    "filename": doc.get("original_filename", ""),
                    "page_count": doc.get("page_count", 0),
                    "summary": doc.get("summary", "")
                }
                for doc in documents
            ],
            "risks": risks
        }

        html_content = self._generate_html(dashboard_data)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save dashboard
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path

    def _generate_html(self, data: Dict) -> str:
        """Generate the HTML content for the dashboard"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Legal Risk Analysis Dashboard - {data["analysis_name"]}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        header {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
            color: white;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        header h1 {{
            font-size: 2rem;
            margin-bottom: 10px;
        }}

        header p {{
            opacity: 0.9;
            font-size: 0.95rem;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
            text-align: center;
        }}

        .metric-card .value {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #1e3a5f;
        }}

        .metric-card .label {{
            color: #666;
            font-size: 0.9rem;
            margin-top: 5px;
        }}

        .metric-card.critical .value {{ color: #dc2626; }}
        .metric-card.high .value {{ color: #ea580c; }}
        .metric-card.medium .value {{ color: #ca8a04; }}
        .metric-card.low .value {{ color: #16a34a; }}

        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .chart-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        }}

        .chart-card h3 {{
            margin-bottom: 20px;
            color: #1e3a5f;
            font-size: 1.1rem;
        }}

        .risk-table-container {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
            overflow: hidden;
            margin-bottom: 30px;
        }}

        .table-header {{
            padding: 20px 25px;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }}

        .table-header h3 {{
            color: #1e3a5f;
            font-size: 1.1rem;
        }}

        .filters {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .filters select, .filters input {{
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 0.9rem;
        }}

        .risk-table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .risk-table th {{
            background: #f9fafb;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #374151;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            cursor: pointer;
        }}

        .risk-table th:hover {{
            background: #f3f4f6;
        }}

        .risk-table td {{
            padding: 15px;
            border-top: 1px solid #e5e7eb;
        }}

        .risk-table tr:hover {{
            background: #f9fafb;
        }}

        .severity-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}

        .severity-critical {{ background: #fef2f2; color: #dc2626; }}
        .severity-high {{ background: #fff7ed; color: #ea580c; }}
        .severity-medium {{ background: #fefce8; color: #ca8a04; }}
        .severity-low {{ background: #f0fdf4; color: #16a34a; }}

        .risk-title {{
            font-weight: 500;
            color: #1e3a5f;
            cursor: pointer;
        }}

        .risk-title:hover {{
            text-decoration: underline;
        }}

        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            overflow-y: auto;
        }}

        .modal.active {{
            display: flex;
            align-items: flex-start;
            justify-content: center;
            padding: 50px 20px;
        }}

        .modal-content {{
            background: white;
            border-radius: 12px;
            max-width: 800px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
        }}

        .modal-header {{
            padding: 25px;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}

        .modal-header h2 {{
            color: #1e3a5f;
            font-size: 1.3rem;
            flex: 1;
        }}

        .modal-close {{
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #6b7280;
            padding: 0 10px;
        }}

        .modal-body {{
            padding: 25px;
        }}

        .detail-section {{
            margin-bottom: 20px;
        }}

        .detail-section h4 {{
            color: #374151;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }}

        .detail-section p {{
            color: #4b5563;
        }}

        .evidence-item {{
            background: #f9fafb;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
        }}

        .evidence-item .citation {{
            font-style: italic;
            color: #6b7280;
            margin-top: 8px;
        }}

        .documents-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }}

        .doc-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        }}

        .doc-card h4 {{
            color: #1e3a5f;
            margin-bottom: 10px;
        }}

        .doc-card p {{
            color: #6b7280;
            font-size: 0.9rem;
        }}

        .tab-container {{
            margin-bottom: 30px;
        }}

        .tabs {{
            display: flex;
            gap: 5px;
            background: white;
            padding: 5px;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
            margin-bottom: 20px;
        }}

        .tab {{
            padding: 12px 24px;
            border: none;
            background: transparent;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            color: #6b7280;
            transition: all 0.2s;
        }}

        .tab.active {{
            background: #1e3a5f;
            color: white;
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        @media (max-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}

            .metrics-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{data["analysis_name"]}</h1>
            <p>Analysis ID: {data["analysis_id"]} | Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </header>

        <div class="metrics-grid" id="metricsGrid"></div>

        <div class="tabs">
            <button class="tab active" onclick="showTab('risks')">Risk Analysis</button>
            <button class="tab" onclick="showTab('documents')">Documents</button>
        </div>

        <div id="risks" class="tab-content active">
            <div class="charts-grid">
                <div class="chart-card">
                    <h3>Risks by Severity</h3>
                    <canvas id="severityChart"></canvas>
                </div>
                <div class="chart-card">
                    <h3>Risks by Category</h3>
                    <canvas id="categoryChart"></canvas>
                </div>
            </div>

            <div class="risk-table-container">
                <div class="table-header">
                    <h3>Risk Register</h3>
                    <div class="filters">
                        <select id="categoryFilter" onchange="filterRisks()">
                            <option value="">All Categories</option>
                            <option value="Contractual">Contractual</option>
                            <option value="Regulatory">Regulatory</option>
                            <option value="Litigation">Litigation</option>
                            <option value="IP">IP</option>
                            <option value="Operational">Operational</option>
                        </select>
                        <select id="severityFilter" onchange="filterRisks()">
                            <option value="">All Severities</option>
                            <option value="Critical">Critical</option>
                            <option value="High">High</option>
                            <option value="Medium">Medium</option>
                            <option value="Low">Low</option>
                        </select>
                        <input type="text" id="searchInput" placeholder="Search risks..." oninput="filterRisks()">
                    </div>
                </div>
                <table class="risk-table">
                    <thead>
                        <tr>
                            <th onclick="sortTable('risk_id')">ID</th>
                            <th onclick="sortTable('title')">Title</th>
                            <th onclick="sortTable('category')">Category</th>
                            <th onclick="sortTable('severity')">Severity</th>
                            <th onclick="sortTable('likelihood')">Likelihood</th>
                        </tr>
                    </thead>
                    <tbody id="riskTableBody"></tbody>
                </table>
            </div>
        </div>

        <div id="documents" class="tab-content">
            <div class="documents-grid" id="documentsGrid"></div>
        </div>
    </div>

    <div class="modal" id="riskModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle"></h2>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body" id="modalBody"></div>
        </div>
    </div>

    <script>
        // Embed data
        const dashboardData = {json.dumps(data, indent=2)};

        // State
        let currentSort = {{ column: null, direction: 'asc' }};
        let filteredRisks = [...dashboardData.risks];

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {{
            renderMetrics();
            renderCharts();
            renderRiskTable();
            renderDocuments();
        }});

        function renderMetrics() {{
            const risks = dashboardData.risks;
            const severityCounts = {{
                Critical: risks.filter(r => r.severity === 'Critical').length,
                High: risks.filter(r => r.severity === 'High').length,
                Medium: risks.filter(r => r.severity === 'Medium').length,
                Low: risks.filter(r => r.severity === 'Low').length
            }};

            const grid = document.getElementById('metricsGrid');
            grid.innerHTML = `
                <div class="metric-card">
                    <div class="value">${{risks.length}}</div>
                    <div class="label">Total Risks</div>
                </div>
                <div class="metric-card critical">
                    <div class="value">${{severityCounts.Critical}}</div>
                    <div class="label">Critical</div>
                </div>
                <div class="metric-card high">
                    <div class="value">${{severityCounts.High}}</div>
                    <div class="label">High</div>
                </div>
                <div class="metric-card medium">
                    <div class="value">${{severityCounts.Medium}}</div>
                    <div class="label">Medium</div>
                </div>
                <div class="metric-card low">
                    <div class="value">${{severityCounts.Low}}</div>
                    <div class="label">Low</div>
                </div>
            `;
        }}

        function renderCharts() {{
            const risks = dashboardData.risks;

            // Severity chart
            const severityCtx = document.getElementById('severityChart').getContext('2d');
            new Chart(severityCtx, {{
                type: 'doughnut',
                data: {{
                    labels: ['Critical', 'High', 'Medium', 'Low'],
                    datasets: [{{
                        data: [
                            risks.filter(r => r.severity === 'Critical').length,
                            risks.filter(r => r.severity === 'High').length,
                            risks.filter(r => r.severity === 'Medium').length,
                            risks.filter(r => r.severity === 'Low').length
                        ],
                        backgroundColor: ['#dc2626', '#ea580c', '#ca8a04', '#16a34a']
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});

            // Category chart
            const categories = ['Contractual', 'Regulatory', 'Litigation', 'IP', 'Operational'];
            const categoryCtx = document.getElementById('categoryChart').getContext('2d');
            new Chart(categoryCtx, {{
                type: 'bar',
                data: {{
                    labels: categories,
                    datasets: [{{
                        label: 'Number of Risks',
                        data: categories.map(cat => risks.filter(r => r.category === cat).length),
                        backgroundColor: '#1e3a5f'
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            display: false
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{
                                stepSize: 1
                            }}
                        }}
                    }}
                }}
            }});
        }}

        function renderRiskTable() {{
            const tbody = document.getElementById('riskTableBody');
            tbody.innerHTML = filteredRisks.map(risk => `
                <tr>
                    <td>${{risk.risk_id}}</td>
                    <td><span class="risk-title" onclick="showRiskDetail('${{risk.risk_id}}')">${{risk.title}}</span></td>
                    <td>${{risk.category}}</td>
                    <td><span class="severity-badge severity-${{risk.severity.toLowerCase()}}">${{risk.severity}}</span></td>
                    <td>${{risk.likelihood}}</td>
                </tr>
            `).join('');
        }}

        function renderDocuments() {{
            const grid = document.getElementById('documentsGrid');
            grid.innerHTML = dashboardData.documents.map(doc => `
                <div class="doc-card">
                    <h4>${{doc.filename}}</h4>
                    <p><strong>ID:</strong> ${{doc.doc_id}}</p>
                    <p><strong>Pages:</strong> ${{doc.page_count}}</p>
                    <p>${{doc.summary || 'No summary available'}}</p>
                </div>
            `).join('');
        }}

        function filterRisks() {{
            const category = document.getElementById('categoryFilter').value;
            const severity = document.getElementById('severityFilter').value;
            const search = document.getElementById('searchInput').value.toLowerCase();

            filteredRisks = dashboardData.risks.filter(risk => {{
                if (category && risk.category !== category) return false;
                if (severity && risk.severity !== severity) return false;
                if (search && !risk.title.toLowerCase().includes(search) &&
                    !risk.description.toLowerCase().includes(search)) return false;
                return true;
            }});

            renderRiskTable();
        }}

        function sortTable(column) {{
            if (currentSort.column === column) {{
                currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
            }} else {{
                currentSort.column = column;
                currentSort.direction = 'asc';
            }}

            filteredRisks.sort((a, b) => {{
                let valA = a[column] || '';
                let valB = b[column] || '';

                if (column === 'severity') {{
                    const order = {{ Critical: 0, High: 1, Medium: 2, Low: 3 }};
                    valA = order[valA] ?? 4;
                    valB = order[valB] ?? 4;
                }}

                if (valA < valB) return currentSort.direction === 'asc' ? -1 : 1;
                if (valA > valB) return currentSort.direction === 'asc' ? 1 : -1;
                return 0;
            }});

            renderRiskTable();
        }}

        function showRiskDetail(riskId) {{
            const risk = dashboardData.risks.find(r => r.risk_id === riskId);
            if (!risk) return;

            document.getElementById('modalTitle').textContent = risk.title;
            document.getElementById('modalBody').innerHTML = `
                <div class="detail-section">
                    <span class="severity-badge severity-${{risk.severity.toLowerCase()}}">${{risk.severity}}</span>
                    <span style="margin-left: 10px; color: #6b7280;">${{risk.category}} | ${{risk.likelihood}}</span>
                </div>
                <div class="detail-section">
                    <h4>Description</h4>
                    <p>${{risk.description}}</p>
                </div>
                ${{risk.evidence && risk.evidence.length > 0 ? `
                <div class="detail-section">
                    <h4>Evidence</h4>
                    ${{risk.evidence.map(ev => `
                        <div class="evidence-item">
                            <strong>${{ev.doc_id}} - Page ${{ev.page_num}}</strong>
                            <div class="citation">"${{ev.citation}}"</div>
                        </div>
                    `).join('')}}
                </div>
                ` : ''}}
                <div class="detail-section">
                    <h4>Legal Basis</h4>
                    <p>${{risk.legal_basis || 'Not specified'}}</p>
                </div>
                <div class="detail-section">
                    <h4>Recommended Mitigation</h4>
                    <p>${{risk.recommended_mitigation || 'Not specified'}}</p>
                </div>
            `;

            document.getElementById('riskModal').classList.add('active');
        }}

        function closeModal() {{
            document.getElementById('riskModal').classList.remove('active');
        }}

        function showTab(tabId) {{
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            event.target.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        }}

        // Close modal on outside click
        document.getElementById('riskModal').addEventListener('click', (e) => {{
            if (e.target.id === 'riskModal') closeModal();
        }});

        // Close modal on escape key
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') closeModal();
        }});
    </script>
</body>
</html>'''


def create_dashboard_generator() -> DashboardGenerator:
    """Factory function to create the dashboard generator"""
    return DashboardGenerator()
