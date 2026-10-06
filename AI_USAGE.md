# AI Usage Documentation

This document describes the role of Artificial Intelligence (AI) tools in designing, implementing, refactoring, and testing the Multi-Source Web Scraping & Data Consolidation Pipeline.

---

## 1. AI Tools Used

| AI Tool | Version / Model | Primary Scope of Usage |
|---|---|---|
| **Google Antigravity / Gemini 3.8 Flash** | Pair Programming AI Assistant | Architecture planning, modular design, selector extraction, unit test generation, error handling implementation |
| **Claude / ChatGPT** | LLM Assisting Concept | Schema standardization design and duplicate normalization strategy |

---

## 2. What Each Tool Was Used For

- **Architecture & System Design:**
  - Designing a decoupled architecture separating scraping (`scrapers/`), data modeling & cleaning (`processing/`), and pipeline orchestration (`pipeline.py`).
  - Formulating a unified common data schema that consolidates disparate e-commerce book records and quote records without inventing fictitious data.
- **HTML Parsing & Selector Discovery:**
  - Analyzing the DOM hierarchies of `https://books.toscrape.com/` and `https://quotes.toscrape.com/`.
  - Handling subtle DOM traps (e.g., truncated text in book title links vs. full title in `title` attribute).
- **Data Transformation & Normalization:**
  - Designing regex routines for currency parsing and multi-format star rating conversions.
  - Designing composite fuzzy deduplication keys (`source::author::text` and `source::title`).
- **Test Generation:**
  - Writing automated pytest fixtures and unit tests covering edge cases in cleaning, validation, and deduplication.
- **Documentation & Packaging:**
  - Drafting comprehensive `README.md` and Docker setup.

---

## 3. Representative Prompts

### Prompt 1: DOM Inspection & Traps
> *"Inspect the book cards on books.toscrape.com. What happens if we extract the anchor text inside `<h3><a href="...">`? Does it truncate long titles? What selector provides the complete untruncated book title?"*

### Prompt 2: Relative URL Resolution & Pagination
> *"On books.toscrape.com, page 1 links to `catalogue/page-2.html`, while page 2 links to `page-3.html`. How should `urllib.parse.urljoin` be structured to guarantee that relative paths resolve correctly regardless of whether the current page is root `index.html` or nested in `catalogue/`?"*

### Prompt 3: Duplicate Normalization Logic
> *"How should we detect duplicates between 'Example Book Title', ' Example Book Title ', and 'EXAMPLE BOOK TITLE!' without relying on exact string equality? Provide a normalization algorithm that handles casing, whitespace, and punctuation variations."*

### Prompt 4: Schema Validation & Funnel Metrics
> *"Design a data validation layer in Python that separates fatal errors (e.g. missing title or invalid URL) from soft warnings, while outputting a structured summary report containing collection funnels and field completeness percentages."*

---

## 4. Code Modules That Were AI-Assisted

1. **`scrapers/books_scraper.py` & `scrapers/quotes_scraper.py`**:
   - Selector definitions and breadcrumb hierarchy parsing for book categories.
   - Dynamic pagination loops detecting the absence of `li.next a`.
2. **`processing/cleaning.py`**:
   - Currency symbol stripping, float casting, and star-rating word mapping (`One`..`Five` -> `1`..`5`).
   - Unicode typographic quotation mark normalization (`“”` -> `"`).
3. **`processing/deduplication.py`**:
   - Regex-based string normalization (`re.sub(r'[^\w\s]', ' ', ...)`) and composite key generation.
4. **`tests/`**:
   - Generating 24 unit and integration test fixtures covering normal, invalid, and boundary test cases.

---

## 5. Important Changes & Corrections Made After Reviewing AI Output

During implementation and manual code review, several AI suggestions required critical adjustments:

1. **Book Title Truncation Trap:**
   - *AI Suggestion:* The initial AI-generated parser used `pod.select_one("h3 a").get_text(strip=True)` to extract book titles.
   - *Issue Discovered:* In `Books to Scrape`, long titles in anchor tags are truncated with an ellipsis (`...`), e.g., `"A Light in the ..."` instead of `"A Light in the Attic"`.
   - *Correction:* Modified the parser to extract `title_link.get("title")` first, falling back to inner text only if the attribute was absent.

2. **Relative URL Resolution Bug:**
   - *AI Suggestion:* Constructing URLs via manual string formatting `f"{base_url}/catalogue/{next_page}"`.
   - *Issue Discovered:* On page 2 (`https://books.toscrape.com/catalogue/page-2.html`), the next button contains `page-3.html`. Appending this resulted in broken URLs like `.../catalogue/catalogue/page-3.html`.
   - *Correction:* Replaced manual concatenation with `urllib.parse.urljoin(current_url, next_href)`, allowing standard RFC 3986 relative URL resolution.

3. **Windows Console Unicode Encoding (`cp1252`):**
   - *AI Suggestion:* Printing raw strings containing British Pound signs (`£`) and curled quotes directly to standard output.
   - *Issue Discovered:* Windows PowerShell environments using code page `cp1252` threw `UnicodeEncodeError: 'charmap' codec can't encode character '\x80'`.
   - *Correction:* Configured explicit UTF-8 encoding across file handlers, output writers, and sanitized string representations.

4. **Attribute Name Mismatch in Deduplication Audit:**
   - *AI Suggestion:* Initially `DuplicateAuditRecord` declared `source_url`, but `test_deduplication.py` attempted to access `duplicate_url`.
   - *Correction:* Added an explicit `@property def duplicate_url(self) -> str` to ensure API consistency without breaking backward compatibility.

---

## 6. Incorrect or Incomplete AI-Generated Suggestions Discovered

- **Synchronous Crawling of 1,000 Detail Pages by Default:**
  - *AI Initial Suggestion:* Crawling all 1,000 book detail pages sequentially in a single synchronous pass.
  - *Why It Was Inappropriate:* At ~1.2s per request, crawling 1,000 detail pages sequentially would take over 20 minutes and risk rate-limiting by the practice server.
  - *Resolution:* Made detail enrichment configurable via `--fetch-details` and `--no-details`, defaulted pagination to `--max-pages 3` for instant reproducible testing, and allowed `--all-pages` for full scraping.

- **Missing Empty String Handling in Cleaners:**
  - *AI Initial Suggestion:* Returning empty strings `""` for missing fields.
  - *Resolution:* Enforced Section 5.2 requirement ("Use appropriate null/empty values when a field does not apply. Do not invent data.") by converting all empty strings and placeholders (`"N/A"`, `"null"`) to `None`.

---

## 7. How the Final Solution Was Tested and Verified

1. **Automated Unit & Integration Testing:**
   - Ran `pytest -v` across 24 test cases in `tests/test_cleaning.py`, `tests/test_validation.py`, `tests/test_deduplication.py`, `tests/test_scrapers.py`, and `tests/test_pipeline.py`.
   - All 24 tests passed in **0.42 seconds** with 100% assertions satisfied.
2. **End-to-End Live Execution:**
   - Executed `python main.py --max-pages 3` against live web targets.
   - Verified that 90 records were successfully scraped, cleaned, validated, and consolidated in **47.42 seconds**.
3. **Output File Verification:**
   - Inspected `output/final_dataset.csv` (108 KB) and verified column headers, numeric conversions, and UTF-8 encoding.
   - Inspected `output/summary_report.json` and verified funnel counts, completeness ratios, and zero validation failures.
   - Inspected `logs/scraper.log` and verified structured log entries.
