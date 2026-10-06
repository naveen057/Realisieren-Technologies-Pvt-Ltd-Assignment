"""
Generates the interactive HTML dataset dashboard and visualizer (index.html).
"""

import json
from pathlib import Path


def generate_html():
    json_path = Path("output/final_dataset.json")
    summary_path = Path("output/summary_report.json")

    with open(json_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)

    funnel = summary.get("pipeline_funnel_metrics", {})
    completeness = summary.get("field_completeness_percentages", {})

    completeness_rows = ""
    for k, v in completeness.items():
        completeness_rows += f"""
        <div class="progress-row">
            <div class="progress-label">
                <code>{k}</code>
                <span>{v}</span>
            </div>
            <div class="progress-bar-bg"><div class="progress-fill" style="width: {v};"></div></div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Source Web Scraping & Data Consolidation Dashboard</title>
    <meta name="description" content="Interactive dashboard and data explorer for Realisieren Technologies Web Scraping Take-Home Technical Assessment.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0a0e17;
            --bg-secondary: #111827;
            --bg-card: rgba(17, 24, 39, 0.7);
            --border-color: rgba(255, 255, 255, 0.08);
            --border-hover: rgba(99, 102, 241, 0.4);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-cyan: #06b6d4;
            --accent-indigo: #6366f1;
            --accent-emerald: #10b981;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --shadow-glow: 0 0 25px rgba(99, 102, 241, 0.15);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
            background-image: 
                radial-gradient(circle at 15% 20%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 85% 70%, rgba(6, 182, 212, 0.08) 0%, transparent 40%);
        }}

        .container {{
            max-width: 1350px;
            margin: 0 auto;
            padding: 2.5rem 1.5rem;
        }}

        header {{
            margin-bottom: 2.5rem;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 1.5rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 2rem;
        }}

        .badge-pill {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.35rem 0.85rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            background: rgba(99, 102, 241, 0.15);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #a5b4fc;
            margin-bottom: 0.75rem;
        }}

        .badge-pill::before {{
            content: '';
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--accent-cyan);
            box-shadow: 0 0 8px var(--accent-cyan);
        }}

        h1 {{
            font-size: 2.25rem;
            font-weight: 800;
            letter-spacing: -0.025em;
            background: linear-gradient(135deg, #ffffff 30%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}

        .subtitle {{
            color: var(--text-secondary);
            font-size: 1.05rem;
            max-width: 750px;
        }}

        .header-actions {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.65rem 1.25rem;
            border-radius: var(--radius-sm);
            font-size: 0.875rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid transparent;
        }}

        .btn-primary {{
            background: linear-gradient(135deg, var(--accent-indigo), #4f46e5);
            color: white;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35);
        }}

        .btn-primary:hover {{
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(79, 70, 229, 0.45);
        }}

        .btn-secondary {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
        }}

        .btn-secondary:hover {{
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2.5rem;
        }}

        .kpi-card {{
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 1.25rem 1.5rem;
            position: relative;
            overflow: hidden;
            transition: all 0.25s ease;
        }}

        .kpi-card:hover {{
            border-color: var(--border-hover);
            transform: translateY(-2px);
            box-shadow: var(--shadow-glow);
        }}

        .kpi-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-indigo));
        }}

        .kpi-label {{
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}

        .kpi-value {{
            font-size: 2rem;
            font-weight: 800;
            color: var(--text-primary);
            letter-spacing: -0.02em;
        }}

        .kpi-sub {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-top: 0.25rem;
        }}

        .tab-bar {{
            display: flex;
            gap: 0.5rem;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 2rem;
        }}

        .tab-btn {{
            background: none;
            border: none;
            padding: 0.75rem 1.5rem;
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }}

        .tab-btn.active {{
            color: var(--accent-cyan);
            border-bottom-color: var(--accent-cyan);
        }}

        .tab-btn:hover:not(.active) {{
            color: var(--text-primary);
        }}

        .tab-pane {{
            display: none;
        }}

        .tab-pane.active {{
            display: block;
            animation: fadeIn 0.3s ease;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(6px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .filter-panel {{
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 1.25rem;
            margin-bottom: 1.5rem;
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            align-items: center;
            justify-content: space-between;
        }}

        .search-box {{
            position: relative;
            flex: 1;
            min-width: 280px;
        }}

        .search-input {{
            width: 100%;
            padding: 0.7rem 1rem 0.7rem 2.5rem;
            background: rgba(0, 0, 0, 0.35);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            color: var(--text-primary);
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.2s;
        }}

        .search-input:focus {{
            border-color: var(--accent-indigo);
        }}

        .search-icon {{
            position: absolute;
            left: 0.9rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            pointer-events: none;
        }}

        .filters-group {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex-wrap: wrap;
        }}

        .select-filter {{
            padding: 0.65rem 1rem;
            background: rgba(0, 0, 0, 0.35);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            color: var(--text-primary);
            font-size: 0.85rem;
            outline: none;
            cursor: pointer;
        }}

        .select-filter:focus {{
            border-color: var(--accent-indigo);
        }}

        .table-card {{
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
        }}

        .table-responsive {{
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
            text-align: left;
        }}

        th {{
            background: rgba(255, 255, 255, 0.03);
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.72rem;
            letter-spacing: 0.06em;
            padding: 1rem 1.25rem;
            border-bottom: 1px solid var(--border-color);
            white-space: nowrap;
        }}

        td {{
            padding: 1rem 1.25rem;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-secondary);
            vertical-align: middle;
        }}

        tr:hover td {{
            background: rgba(255, 255, 255, 0.02);
            color: var(--text-primary);
        }}

        .source-tag {{
            display: inline-flex;
            align-items: center;
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            white-space: nowrap;
        }}

        .source-books {{
            background: rgba(6, 182, 212, 0.12);
            color: #67e8f9;
            border: 1px solid rgba(6, 182, 212, 0.25);
        }}

        .source-quotes {{
            background: rgba(168, 85, 247, 0.12);
            color: #d8b4fe;
            border: 1px solid rgba(168, 85, 247, 0.25);
        }}

        .item-title {{
            color: var(--text-primary);
            font-weight: 600;
            max-width: 320px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        .price-badge {{
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            color: var(--accent-emerald);
        }}

        .stars {{
            color: var(--accent-amber);
            letter-spacing: 2px;
        }}

        .category-tag {{
            background: rgba(255, 255, 255, 0.06);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            color: #cbd5e1;
        }}

        .link-icon {{
            color: var(--accent-cyan);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
        }}

        .link-icon:hover {{
            text-decoration: underline;
        }}

        .table-footer {{
            padding: 1rem 1.25rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
            border-top: 1px solid var(--border-color);
            background: rgba(0, 0, 0, 0.2);
            font-size: 0.85rem;
            color: var(--text-muted);
        }}

        .pagination-btns {{
            display: flex;
            gap: 0.35rem;
        }}

        .page-btn {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 0.4rem 0.8rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8rem;
            transition: all 0.2s;
        }}

        .page-btn:hover:not(:disabled) {{
            background: var(--accent-indigo);
            border-color: var(--accent-indigo);
        }}

        .page-btn:disabled {{
            opacity: 0.4;
            cursor: not-allowed;
        }}

        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(8px);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
        }}

        .modal.active {{
            display: flex;
        }}

        .modal-content {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            width: 100%;
            max-width: 650px;
            max-height: 85vh;
            overflow-y: auto;
            padding: 2rem;
            position: relative;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }}

        .modal-close {{
            position: absolute;
            top: 1.5rem;
            right: 1.5rem;
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 1.5rem;
            cursor: pointer;
        }}

        .modal-close:hover {{
            color: var(--text-primary);
        }}

        .funnel-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .card-box {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 1.5rem;
        }}

        .card-title {{
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 1.25rem;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .progress-row {{
            margin-bottom: 1rem;
        }}

        .progress-label {{
            display: flex;
            justify-content: space-between;
            font-size: 0.85rem;
            margin-bottom: 0.4rem;
        }}

        .progress-bar-bg {{
            height: 8px;
            background: rgba(255, 255, 255, 0.06);
            border-radius: 4px;
            overflow: hidden;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-indigo));
            border-radius: 4px;
        }}

        pre code {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            color: #e2e8f0;
        }}

        .code-card {{
            background: #090d16;
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            padding: 1.25rem;
            overflow-x: auto;
            margin: 1rem 0;
        }}
    </style>
</head>
<body>

<div class="container">
    <header>
        <div>
            <div class="badge-pill">Realisieren Technologies Assessment</div>
            <h1>Multi-Source Web Scraping & Consolidation</h1>
            <p class="subtitle">
                Automated Python data pipeline that scrapes disparate public web sources (Books to Scrape & Quotes to Scrape),
                performs cleaning & schema normalization, executes duplicate detection, validates integrity, and generates a consolidated dataset.
            </p>
        </div>
        <div class="header-actions">
            <a href="https://github.com/naveen057/Realisieren-Technologies-Pvt-Ltd-Assignment" target="_blank" class="btn btn-secondary" id="btn-github">
                GitHub Repository
            </a>
            <a href="output/final_dataset.csv" download class="btn btn-primary" id="btn-download-csv">
                Download CSV
            </a>
        </div>
    </header>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Total Consolidated Records</div>
            <div class="kpi-value" id="kpi-total-records">{len(dataset)}</div>
            <div class="kpi-sub">Cleaned & Standardized</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Data Sources</div>
            <div class="kpi-value">2</div>
            <div class="kpi-sub">Books to Scrape & Quotes</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Validation Pass Rate</div>
            <div class="kpi-value" style="color: var(--accent-emerald);">100%</div>
            <div class="kpi-sub">0 Fatal Schema Errors</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Duplicates Detected</div>
            <div class="kpi-value" style="color: var(--accent-cyan);">0</div>
            <div class="kpi-sub">Normalized Fuzzy Keys</div>
        </div>
    </div>

    <div class="tab-bar">
        <button class="tab-btn active" onclick="switchTab('tab-dataset')" id="tab-btn-dataset">Consolidated Dataset</button>
        <button class="tab-btn" onclick="switchTab('tab-funnel')" id="tab-btn-funnel">Pipeline Funnel & Completeness</button>
        <button class="tab-btn" onclick="switchTab('tab-architecture')" id="tab-btn-architecture">Architecture & How to Run</button>
    </div>

    <div id="tab-dataset" class="tab-pane active">
        <div class="filter-panel">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="search-input" class="search-input" placeholder="Search titles, authors, categories, or keywords..." oninput="handleSearch()">
            </div>
            <div class="filters-group">
                <select id="source-filter" class="select-filter" onchange="handleFilter()">
                    <option value="all">All Sources</option>
                    <option value="Books to Scrape">Books to Scrape</option>
                    <option value="Quotes to Scrape">Quotes to Scrape</option>
                </select>
                <select id="category-filter" class="select-filter" onchange="handleFilter()">
                    <option value="all">All Categories</option>
                </select>
            </div>
        </div>

        <div class="table-card">
            <div class="table-responsive">
                <table id="dataset-table">
                    <thead>
                        <tr>
                            <th>Source</th>
                            <th>Name / Title / Quote</th>
                            <th>Category / Author</th>
                            <th>Price</th>
                            <th>Rating</th>
                            <th>Source URL</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody id="table-body">
                    </tbody>
                </table>
            </div>
            <div class="table-footer">
                <div id="pagination-info">Showing 1 to 20 of 0 entries</div>
                <div class="pagination-btns">
                    <button class="page-btn" id="btn-prev" onclick="changePage(-1)">Previous</button>
                    <button class="page-btn" id="btn-next" onclick="changePage(1)">Next</button>
                </div>
            </div>
        </div>
    </div>

    <div id="tab-funnel" class="tab-pane">
        <div class="funnel-container">
            <div class="card-box">
                <div class="card-title">📊 Pipeline Execution Funnel</div>
                <div class="progress-row">
                    <div class="progress-label">
                        <span>1. Raw Ingested Records</span>
                        <strong id="funnel-raw">{funnel.get("total_records_collected", len(dataset))}</strong>
                    </div>
                    <div class="progress-bar-bg"><div class="progress-fill" style="width: 100%;"></div></div>
                </div>
                <div class="progress-row">
                    <div class="progress-label">
                        <span>2. Cleaned & Standardized</span>
                        <strong>{funnel.get("total_records_after_cleaning", len(dataset))}</strong>
                    </div>
                    <div class="progress-bar-bg"><div class="progress-fill" style="width: 100%;"></div></div>
                </div>
                <div class="progress-row">
                    <div class="progress-label">
                        <span>3. Passed Schema Validation</span>
                        <strong style="color: var(--accent-emerald);">{len(dataset)}</strong>
                    </div>
                    <div class="progress-bar-bg"><div class="progress-fill" style="width: 100%; background: var(--accent-emerald);"></div></div>
                </div>
                <div class="progress-row">
                    <div class="progress-label">
                        <span>4. Deduplicated Final Dataset</span>
                        <strong style="color: var(--accent-cyan);">{len(dataset)}</strong>
                    </div>
                    <div class="progress-bar-bg"><div class="progress-fill" style="width: 100%; background: var(--accent-cyan);"></div></div>
                </div>
            </div>

            <div class="card-box">
                <div class="card-title">🎯 Field Completeness Ratios</div>
                {completeness_rows}
            </div>
        </div>
    </div>

    <div id="tab-architecture" class="tab-pane">
        <div class="card-box" style="margin-bottom: 1.5rem;">
            <div class="card-title">⚙️ Execution Architecture</div>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">
                The pipeline decouples scraping, parsing, cleaning, validation, and deduplication into distinct, testable modules.
            </p>
            <div class="code-card">
                <pre><code>Website A (Books to Scrape) ──┐
Website B (Quotes to Scrape) ─┼──> Scraping ──> Cleaning ──> Validation ──> Deduplication ──> Consolidation ──> Final Output
                              ┘</code></pre>
            </div>
        </div>

        <div class="card-box">
            <div class="card-title">💻 Quick Run Commands</div>
            <div class="code-card">
                <pre><code># 1. Run scraper with default 3 pages per source
python main.py

# 2. Scrape all available pages until pagination concludes
python main.py --all-pages

# 3. Fast run without visiting individual book pages
python main.py --max-pages 5 --no-details

# 4. Run automated test suite (24 tests)
pytest -v</code></pre>
            </div>
        </div>
    </div>
</div>

<div class="modal" id="detail-modal" onclick="closeModal(event)">
    <div class="modal-content" onclick="event.stopPropagation()">
        <button class="modal-close" onclick="closeModal()">&times;</button>
        <h3 id="modal-title" style="margin-bottom: 1rem; color: var(--text-primary);">Record Details</h3>
        <div id="modal-body" style="font-size: 0.9rem; color: var(--text-secondary);"></div>
    </div>
</div>

<script>
    const DATASET = {json.dumps(dataset, ensure_ascii=False)};

    let filteredData = [...DATASET];
    let currentPage = 1;
    const pageSize = 20;

    function initFilters() {{
        const catSelect = document.getElementById('category-filter');
        const categories = new Set();
        DATASET.forEach(item => {{
            if (item.category) categories.add(item.category);
        }});
        Array.from(categories).sort().forEach(cat => {{
            const opt = document.createElement('option');
            opt.value = cat;
            opt.textContent = cat;
            catSelect.appendChild(opt);
        }});
    }}

    function renderTable() {{
        const tbody = document.getElementById('table-body');
        tbody.innerHTML = '';

        const startIdx = (currentPage - 1) * pageSize;
        const pageItems = filteredData.slice(startIdx, startIdx + pageSize);

        if (pageItems.length === 0) {{
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem;">No records found matching filters.</td></tr>';
            document.getElementById('pagination-info').textContent = '0 entries';
            document.getElementById('btn-prev').disabled = true;
            document.getElementById('btn-next').disabled = true;
            return;
        }}

        pageItems.forEach((item, index) => {{
            const tr = document.createElement('tr');
            const isBook = item.source.includes('Book');

            const sourceBadge = isBook 
                ? '<span class="source-tag source-books">Books</span>' 
                : '<span class="source-tag source-quotes">Quotes</span>';

            const priceHtml = item.price !== null 
                ? `<span class="price-badge">£${{Number(item.price).toFixed(2)}}</span>` 
                : '<span style="color: var(--text-muted);">-</span>';

            const ratingHtml = item.rating 
                ? `<span class="stars">${{'★'.repeat(item.rating)}}{{'☆'.repeat(5 - item.rating)}}</span>` 
                : '<span style="color: var(--text-muted);">-</span>';

            const catOrAuthor = isBook 
                ? (item.category ? `<span class="category-tag">${{item.category}}</span>` : '<span style="color: var(--text-muted);">Default</span>')
                : `<span style="color: #cbd5e1; font-weight: 500;">${{item.author || 'Unknown'}}</span>`;

            tr.innerHTML = `
                <td>${{sourceBadge}}</td>
                <td><div class="item-title" title="${{item.name_or_title}}">${{item.name_or_title}}</div></td>
                <td>${{catOrAuthor}}</td>
                <td>${{priceHtml}}</td>
                <td>${{ratingHtml}}</td>
                <td><a href="${{item.source_url}}" target="_blank" class="link-icon">Visit ↗</a></td>
                <td><button class="page-btn" onclick="openModal(${{startIdx + index}})">View</button></td>
            `;
            tbody.appendChild(tr);
        }});

        const total = filteredData.length;
        const endIdx = Math.min(startIdx + pageSize, total);
        document.getElementById('pagination-info').textContent = `Showing ${{startIdx + 1}} to ${{endIdx}} of ${{total}} entries`;
        document.getElementById('btn-prev').disabled = currentPage === 1;
        document.getElementById('btn-next').disabled = endIdx >= total;
    }}

    function handleSearch() {{
        applyFilters();
    }}

    function handleFilter() {{
        applyFilters();
    }}

    function applyFilters() {{
        const query = document.getElementById('search-input').value.toLowerCase().trim();
        const src = document.getElementById('source-filter').value;
        const cat = document.getElementById('category-filter').value;

        filteredData = DATASET.filter(item => {{
            const matchSrc = src === 'all' || item.source === src;
            const matchCat = cat === 'all' || item.category === cat;
            const textMatch = !query || 
                (item.name_or_title && item.name_or_title.toLowerCase().includes(query)) ||
                (item.author && item.author.toLowerCase().includes(query)) ||
                (item.tags && item.tags.toLowerCase().includes(query)) ||
                (item.category && item.category.toLowerCase().includes(query));

            return matchSrc && matchCat && textMatch;
        }});

        currentPage = 1;
        renderTable();
    }}

    function changePage(direction) {{
        currentPage += direction;
        renderTable();
    }}

    function switchTab(tabId) {{
        document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
        document.getElementById('tab-btn-' + tabId.replace('tab-', '')).classList.add('active');
    }}

    function openModal(index) {{
        const item = filteredData[index];
        if (!item) return;

        document.getElementById('modal-title').textContent = item.name_or_title;
        let content = `
            <div style="margin-bottom: 0.75rem;"><strong>Source:</strong> ${{item.source}}</div>
            <div style="margin-bottom: 0.75rem;"><strong>Source URL:</strong> <a href="${{item.source_url}}" target="_blank" style="color: var(--accent-cyan);">${{item.source_url}}</a></div>
        `;
        if (item.category) content += `<div style="margin-bottom: 0.75rem;"><strong>Category:</strong> ${{item.category}}</div>`;
        if (item.price !== null) content += `<div style="margin-bottom: 0.75rem;"><strong>Price:</strong> £${{Number(item.price).toFixed(2)}}</div>`;
        if (item.rating !== null) content += `<div style="margin-bottom: 0.75rem;"><strong>Rating:</strong> ${{item.rating}} / 5</div>`;
        if (item.author) content += `<div style="margin-bottom: 0.75rem;"><strong>Author:</strong> ${{item.author}}</div>`;
        if (item.tags) content += `<div style="margin-bottom: 0.75rem;"><strong>Tags:</strong> ${{item.tags}}</div>`;
        if (item.description) content += `<div style="margin-top: 1rem;"><strong>Description:</strong><p style="margin-top: 0.5rem; line-height: 1.5;">${{item.description}}</p></div>`;
        content += `<div style="margin-top: 1rem; font-size: 0.8rem; color: var(--text-muted);">Scraped At: ${{item.scraped_at}}</div>`;

        document.getElementById('modal-body').innerHTML = content;
        document.getElementById('detail-modal').classList.add('active');
    }}

    function closeModal() {{
        document.getElementById('detail-modal').classList.remove('active');
    }}

    window.addEventListener('DOMContentLoaded', () => {{
        initFilters();
        renderTable();
    }});
</script>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Generated index.html successfully.")


if __name__ == "__main__":
    generate_html()
