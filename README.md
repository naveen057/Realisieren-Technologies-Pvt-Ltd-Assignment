# Realisieren-Technologies-Pvt-Ltd-Assignment
## Multi-Source Web Scraping & Data Consolidation Pipeline

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-24%20passed-brightgreen.svg)]()
[![Code Architecture](https://img.shields.io/badge/architecture-modular-orange.svg)]()

> A robust, fault-tolerant Python data pipeline that scrapes disparate public web sources, standardizes and cleans the ingested records into a unified common schema, detects and handles duplicates, performs schema validation, and outputs a consolidated dataset with detailed execution reporting.

---

## Table of Contents
1. [Assignment & Project Overview](#1-assignment--project-overview)
2. [Python Version & Environment](#2-python-version--environment)
3. [Installation & Setup Instructions](#3-installation--setup-instructions)
4. [Dependencies](#4-dependencies)
5. [How to Run the Scraper (CLI Guide)](#5-how-to-run-the-scraper-cli-guide)
6. [How Pagination Works](#6-how-pagination-works)
7. [Unified Data Model](#7-unified-data-model)
8. [Data Cleaning Approach](#8-data-cleaning-approach)
9. [Data Validation Approach](#9-data-validation-approach)
10. [Duplicate Detection & Resolution Strategy](#10-duplicate-detection--resolution-strategy)
11. [Error Handling & Reliability](#11-error-handling--reliability)
12. [Output Files Description](#12-output-files-description)
13. [Assumptions](#13-assumptions)
14. [Known Limitations](#14-known-limitations)
15. [Bonus Features Implemented](#15-bonus-features-implemented)
16. [AI Usage Summary](#16-ai-usage-summary)

---

## 1. Assignment & Project Overview

This project was built for the **Medium-Level Take-Home Technical Assessment: Multi-Source Web Scraping & Data Consolidation**.

### Architecture & Pipeline Workflow

```
┌─────────────────────────────────┐       ┌──────────────────────────────────┐
│   Source 1: Books to Scrape     │       │    Source 2: Quotes to Scrape    │
│   (https://books.toscrape.com/) │       │   (https://quotes.toscrape.com/) │
└────────────────┬────────────────┘       └─────────────────┬────────────────┘
                 │                                          │
                 ▼                                          ▼
          [BooksScraper]                             [QuotesScraper]
          • Pagination Loop                          • Pagination Loop
          • Pod Extraction                           • Quote / Tag Parsing
          • Detail Enrichment                        • Canonical Anchors
                 │                                          │
                 └────────────────────┬─────────────────────┘
                                      ▼
                           [Raw Records Collection]
                                      │
                                      ▼
                         [Stage 2: Cleaning & Normalization]
                         • Whitespace & Typographic Quotes
                         • Currency Extraction & Float Casting
                         • Star Ratings Word -> Int Conversion
                         • Relative -> Absolute URL Resolution
                                      │
                                      ▼
                         [Stage 3: Validation Engine]
                         • Schema & Required Fields Check
                         • Range Verification (Rating: 1-5, Price >= 0)
                         • URL Format Verification
                         • Partition: Valid Records vs. Rejected
                                      │
                                      ▼
                         [Stage 4: Deduplication Engine]
                         • Case/Punctuation-Insensitive Composite Keys
                         • Strategy: 'remove' (filter) or 'flag' (annotate)
                         • Audit Trail Tracking
                                      │
                                      ▼
                         [Stage 5: Consolidation & Export]
                         ├── output/final_dataset.csv
                         ├── output/final_dataset.json
                         ├── output/summary_report.json
                         └── logs/scraper.log
```

---

## 2. Python Version & Environment

- **Python Version:** Tested and verified on **Python 3.10+** (specifically executed and tested on **Python 3.14.7**).
- **Cross-Platform:** Fully compatible with Windows, macOS, and Linux.

---

## 3. Installation & Setup Instructions

### Option A: Local Virtual Environment Setup (Recommended)

1. **Clone or unzip the project repository:**
   ```bash
   cd Assessment
   ```

2. **Create a virtual environment:**
   ```bash
   # On Windows (PowerShell):
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # On macOS/Linux:
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Option B: Docker Setup (Containerized)

The repository includes a ready-to-use Docker configuration:

```bash
# Build and run with default settings (3 pages per source)
docker compose up --build

# Run with custom arguments
docker run --rm -v $(pwd)/output:/app/output assessment-scraper --max-pages 5 --rate-limit 0.3
```

---

## 4. Dependencies

The project maintains a lightweight and robust dependency footprint:

| Dependency | Purpose |
|---|---|
| `requests>=2.31.0` | HTTP client with connection pooling and session management |
| `beautifulsoup4>=4.12.0` | Resilient HTML DOM parser for extracting structured tags |
| `urllib3>=2.0.0` | Robust exponential backoff retry adapter |
| `pytest>=7.4.0` | Comprehensive unit and integration test runner |

---

## 5. How to Run the Scraper (CLI Guide)

The pipeline is managed via the CLI entrypoint [main.py](file:///c:/Users/Naveen/Desktop/Assessment/main.py):

### Basic Run
Runs the full pipeline across both sources for the first 3 pages with book detail enrichment:
```bash
python main.py
```

### Full Run (All Pages)
Scrapes every page until pagination concludes (50 pages for Books, 10 pages for Quotes):
```bash
python main.py --all-pages
```

### Fast Run (Without Detail Enrichment)
Scrapes catalog listing cards without visiting individual detail pages:
```bash
python main.py --max-pages 5 --no-details
```

### Custom Source Selection
Scrape only Quotes:
```bash
python main.py --sources quotes --max-pages 5
```
Scrape only Books:
```bash
python main.py --sources books --max-pages 2
```

### CLI Options Reference

| Flag | Type | Default | Description |
|---|---|---|---|
| `--sources` | List | `books quotes` | Sources to scrape (`books`, `quotes`, or both) |
| `--max-pages` | Integer | `3` | Maximum pages to scrape per source (pass `0` for all) |
| `--all-pages` | Flag | `False` | Scrapes all available pages until completion |
| `--rate-limit` | Float | `0.2` | Polite sleep delay in seconds between HTTP requests |
| `--fetch-details` | Flag | `True` | Visits individual book detail pages for category & description |
| `--no-details` | Flag | `False` | Disables detail page visits for maximum throughput |
| `--dedup-action` | String | `remove` | Duplicate action: `remove` (filter out) or `flag` (keep with `is_duplicate=True`) |
| `--output-dir` | String | `output` | Directory where CSV and JSON reports will be saved |
| `--logs-dir` | String | `logs` | Directory where `scraper.log` will be saved |
| `--log-level` | String | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

### Running the Test Suite
Run the 24 automated unit and integration tests:
```bash
pytest -v
```

---

## 6. How Pagination Works

Rather than hard-coding URLs, both scrapers implement **dynamic next-button detection**:

1. **Books to Scrape (`https://books.toscrape.com/`)**:
   - The pager contains: `<li class="next"><a href="...">next</a></li>`.
   - On the homepage (`/index.html`), the link points to `catalogue/page-2.html`.
   - On catalog pages (`/catalogue/page-2.html`), the link points to `page-3.html`.
   - The scraper employs `urllib.parse.urljoin(current_page_url, next_href)`. This standard RFC 3986 resolution correctly converts both relative forms to valid absolute URLs (`https://books.toscrape.com/catalogue/page-3.html`).
   - On the final page (Page 50), the `<li class="next">` element is absent, causing the loop to terminate gracefully.

2. **Quotes to Scrape (`https://quotes.toscrape.com/`)**:
   - The pager contains: `<li class="next"><a href="/page/2/">Next</a></li>`.
   - The link is joined using `urljoin(current_url, next_href)`.
   - On the final page (Page 10), the next button disappears, terminating the loop.

---

## 7. Unified Data Model

The pipeline maps raw inputs into a common, standardized schema [StandardRecord](file:///c:/Users/Naveen/Desktop/Assessment/processing/models.py):

| Field | Type | Books to Scrape | Quotes to Scrape | Description / Format |
|---|---|---|---|---|
| `source` | string | `"Books to Scrape"` | `"Quotes to Scrape"` | Origin website name |
| `name_or_title` | string | Book title | Quote text | Primary name or quoted text |
| `category` | string / null | Category (e.g. "Poetry") | `null` | Extracted from breadcrumbs |
| `price` | float / null | Numeric price (e.g. `51.77`) | `null` | Cleaned decimal number in GBP |
| `rating` | integer / null| Star rating integer `1` to `5` | `null` | Converted star rating |
| `author` | string / null | `null` | Author (e.g. "Albert Einstein") | Name of the author |
| `tags` | string / null | `null` | Comma-separated tags | Joined unique tag list |
| `description` | string / null | Product description | `null` | Full descriptive text |
| `source_url` | string | Canonical product URL | Canonical quote URL (`#quote-N`) | Fully qualified source URL |
| `scraped_at` | string | ISO-8601 UTC timestamp | ISO-8601 UTC timestamp | e.g. `2026-10-06T17:08:14.466138+00:00` |

*Note: In compliance with Section 5.2 ("Do not invent data"), fields that do not apply to a source are populated with `null` / empty values.*

---

## 8. Data Cleaning Approach

All transformations are isolated in [processing/cleaning.py](file:///c:/Users/Naveen/Desktop/Assessment/processing/cleaning.py):

1. **Whitespace Normalization:**
   - Strips leading and trailing whitespace.
   - Collapses internal runs of spaces, tabs, and newlines (`\s+`) into a single space.
2. **Typographic & Unicode Cleaning:**
   - Normalizes text with `unicodedata.normalize('NFKC')`.
   - Converts typographic/curly quotes (`“”„‟«»`) into standard ASCII quotes (`"`).
   - Converts curled apostrophes (`‘’‚‛\``) into standard ASCII apostrophes (`'`).
   - Unescapes HTML entities using `html.unescape()` (`&amp;` -> `&`, `&quot;` -> `"`).
3. **Numeric Price Conversion:**
   - Removes currency symbols (`£`, `Â£`, `$`, `€`) and thousands commas.
   - Parses the numeric value using regex `r'(\d+(?:\.\d+)?)'`.
   - Converts `"Free"` to `0.0`.
   - Casts to a float rounded to 2 decimal places.
4. **Rating Standardization:**
   - Translates word-based ratings (`"One"`, `"Two"`, `"Three"`, `"Four"`, `"Five"`) into integers `1` to `5`.
   - Parses CSS class lists (e.g., `["star-rating", "Three"]` -> `3`).
   - Handles numeric strings (`"4/5"`, `"4"`, `4.0` -> `4`).
5. **Tags Normalization:**
   - Strips individual tags, eliminates duplicates while preserving order, and formats as a clean comma-separated string (`"change, thinking, world"`).
6. **Missing Value Standardization:**
   - Sentinel values such as `""`, `"N/A"`, `"null"`, `"none"`, and `"undefined"` are converted to `None`.

---

## 9. Data Validation Approach

All records pass through the [Validator](file:///c:/Users/Naveen/Desktop/Assessment/processing/validation.py) before reaching the final dataset:

1. **Mandatory Field Checks:**
   - `source`: Must be non-empty and match recognized sources.
   - `name_or_title`: Must be present, non-empty, and at least 1 character.
   - `source_url`: Must be a valid HTTP/HTTPS URL with a resolvable network location.
2. **Data Range & Type Checks:**
   - `price`: If present, must be numeric float $\ge 0.0$.
   - `rating`: If present, must be an integer between $1$ and $5$.
3. **Error vs. Warning Segregation:**
   - **Fatal Errors:** Cause record rejection (e.g. missing title, invalid URL, negative price). Rejected records are logged and included in the `validation_failures` audit section of `summary_report.json`.
   - **Non-Fatal Warnings:** Logged for reviewer inspection without rejecting the record (e.g. missing quote author, price over 100,000).

---

## 10. Duplicate Detection & Resolution Strategy

Exact string comparison is insufficient because titles and text can differ in casing, punctuation, and whitespace.

### Normalization Logic
Before matching, comparison text is processed via `normalize_for_comparison()`:
- Converts to lowercase.
- Strips apostrophes (`don't` -> `dont`).
- Replaces punctuation and symbols with whitespace (`re.sub(r'[^\w\s]', ' ', s)`).
- Collapses whitespace into single spaces.
- **Example:** `"Example Book Title"`, `" Example Book Title "`, and `"EXAMPLE BOOK TITLE!"` all reduce to identical key: `"example book title"`.

### Composite Key Strategy
- **Books:** Keyed by `books::{normalized_title}`.
- **Quotes:** Keyed by `quotes::{normalized_author}::{normalized_quote_text[:150]}`.

### Deduplication Action (`--dedup-action`)
- **`remove` (Default):** Retains the first occurrence of each unique key; drops subsequent duplicate records from the final dataset.
- **`flag`:** Retains all records in the final dataset, annotating duplicates with `is_duplicate = True` and recording the original URL in `duplicate_of`.
- **Audit Trail:** Every detected duplicate is cataloged with source, name, duplicate URL, original URL, and action taken in `summary_report.json`.

---

## 11. Error Handling & Reliability

- **Exponential Backoff Retries:** Configured via `urllib3.util.retry.Retry` mounting on `http://` and `https://`. Automatically retries transient network errors and server errors (`429`, `500`, `502`, `503`, `504`) with a customizable `backoff_factor`.
- **Polite Rate Limiting:** Built-in `time.sleep(rate_limit_delay)` ensures respectful scraping rates without overwhelming the hosts.
- **Missing Element Fallbacks:** BeautifulSoup queries use defensive lookups (`pod.select_one(...)`) with fallback defaults, preventing `AttributeError` from terminating the run.
- **Dual Logging:** Simultaneous logging to console and `logs/scraper.log` with UTF-8 encoding prevents `UnicodeEncodeError` in Windows shells.

---

## 12. Output Files Description

When execution completes, outputs are saved to the `output/` directory:

1. **`output/final_dataset.csv`**:
   The primary consolidated tabular dataset with UTF-8 encoding. Contains all records across both sources according to the standardized schema.
2. **`output/final_dataset.json`**:
   JSON array export of the consolidated dataset with complete typing and nested records.
3. **`output/summary_report.json`**:
   Structured metrics document capturing:
   - Pipeline metadata (runtime, timestamps, configurations)
   - Source-specific metrics (pages scraped, raw records extracted, final records by source)
   - Funnel metrics (collected -> cleaned -> rejected -> deduplicated -> final count)
   - Field completeness percentages for each column
   - Validation failure audit log
   - Duplicate detection audit log
   - Network errors encountered
4. **`logs/scraper.log`**:
   Comprehensive timestamped logs tracking each page request, data parse event, warning, and summary milestone.

---

## 13. Assumptions

1. **Books Taxonomy:** Categories and descriptions are located exclusively on individual book detail pages. The scraper extracts them via detail enrichment when `--fetch-details` is enabled.
2. **Quote Identifiers:** Individual quotes on Quotes to Scrape do not possess individual permalink URLs; canonical anchors (`#quote-N`) on the respective page URL are assigned as unique source URLs.
3. **Currency:** Books to Scrape prices are denominated in British Pounds (`£`), converted directly to numeric floats without arbitrary exchange rate alterations.

---

## 14. Known Limitations

1. **Sequential Detail Enrichment:** While listing pages are fetched efficiently, visiting individual book detail pages sequentially with polite delays introduces network latency. Concurrency can be leveraged for higher throughput in production.
2. **Static HTML Focus:** Both target websites render static server-side HTML. Dynamic client-side Single Page Applications (SPAs) requiring JavaScript rendering would require headless browser drivers (e.g., Playwright).

---

## 15. Bonus Features Implemented

- [x] **Configurable CLI Settings:** Comprehensive `argparse` CLI with granular options (`--sources`, `--max-pages`, `--all-pages`, `--rate-limit`, `--fetch-details`, `--dedup-action`, `--log-level`).
- [x] **Exponential Backoff Retries:** `urllib3.util.retry.Retry` with configurable backoff factor and HTTP status code filtering.
- [x] **Polite Rate Limiting:** Configurable sleep delay between requests (`--rate-limit`).
- [x] **Comprehensive Unit & Integration Test Suite:** 24 pytest cases covering scrapers, cleaners, validators, deduplicators, and end-to-end pipeline execution.
- [x] **Data Quality & Completeness Report:** Automatically calculated column completeness percentages in `summary_report.json`.
- [x] **Docker & Docker Compose Integration:** Containerized deployment with volume mounts for reproducible execution in any environment.
- [x] **Dual Export Formats:** Outputs both CSV and JSON formats out-of-the-box.
