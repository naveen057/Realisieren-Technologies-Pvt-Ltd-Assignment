"""
Pipeline Configuration Module.

Defines global and runtime configurations for the multi-source web scraping,
cleaning, validation, and deduplication pipeline.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ScraperConfig:
    """Configuration settings for web scraping and data consolidation pipeline."""

    # Target source URLs
    books_base_url: str = "https://books.toscrape.com/"
    quotes_base_url: str = "https://quotes.toscrape.com/"

    # Pagination controls (None = scrape all pages until the end)
    max_pages: Optional[int] = None

    # Polite rate limiting & networking
    rate_limit_delay: float = 0.3  # seconds between HTTP requests
    request_timeout: int = 15      # seconds
    max_retries: int = 3           # HTTP retry attempts
    backoff_factor: float = 0.5    # exponential backoff multiplier
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 (AssessmentBot/1.0)"
    )

    # Scraper features
    fetch_book_details: bool = True  # whether to visit individual book pages for category & description

    # Pipeline output and directories
    output_dir: str = "output"
    logs_dir: str = "logs"
    dataset_filename: str = "final_dataset.csv"
    summary_filename: str = "summary_report.json"

    # Deduplication strategy: "remove" (drop duplicates) or "flag" (keep & mark is_duplicate)
    dedup_action: str = "remove"

    # Export formats
    export_formats: List[str] = field(default_factory=lambda: ["csv", "json"])

    # Logging level: DEBUG, INFO, WARNING, ERROR
    log_level: str = "INFO"

    @property
    def output_path(self) -> Path:
        """Returns resolved Path object for output directory."""
        return Path(self.output_dir)

    @property
    def logs_path(self) -> Path:
        """Returns resolved Path object for logs directory."""
        return Path(self.logs_dir)

    def ensure_directories(self) -> None:
        """Creates output and log directories if they do not exist."""
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)
