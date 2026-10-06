"""
Quotes to Scrape Web Scraper.

Extracts quotes, authors, and tags across pages from https://quotes.toscrape.com/.
Handles pagination, robust element parsing, and error recovery.
"""

import logging
from typing import List, Optional, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from config import ScraperConfig
from processing.models import RawRecord
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class QuotesScraper(BaseScraper):
    """Scraper implementation for Quotes to Scrape (https://quotes.toscrape.com/)."""

    SOURCE_NAME = "Quotes to Scrape"

    def __init__(self, config: Optional[ScraperConfig] = None):
        super().__init__(config)
        self.start_url = self.config.quotes_base_url

    def scrape(self) -> List[RawRecord]:
        """
        Executes full pagination loop for Quotes to Scrape.
        Stops when next page is absent or max_pages limit is reached.
        """
        records: List[RawRecord] = []
        current_url: Optional[str] = self.start_url
        page_num = 1

        logger.info(f"Starting Quotes scraping from: {current_url}")

        while current_url:
            if self.config.max_pages and page_num > self.config.max_pages:
                logger.info(f"Reached maximum pages limit ({self.config.max_pages}) for Quotes.")
                break

            logger.info(f"[Quotes to Scrape] Scraping Page {page_num}: {current_url}")
            page_records, next_url = self.scrape_page(current_url)

            if not page_records and next_url is None:
                logger.warning(f"No records and no next link found on page {page_num}; stopping.")
                break

            records.extend(page_records)
            self.pages_scraped += 1
            self.items_scraped += len(page_records)

            page_num += 1
            current_url = next_url

        logger.info(
            f"Completed Quotes scraping: {len(records)} records from {self.pages_scraped} pages."
        )
        return records

    def scrape_page(self, url: str) -> Tuple[List[RawRecord], Optional[str]]:
        """
        Scrapes a single listing page of Quotes to Scrape.

        Returns:
            (records, next_page_url)
        """
        response = self.fetch_url(url)
        if not response:
            logger.error(f"Failed to fetch quotes listing page: {url}")
            return [], None

        soup = BeautifulSoup(response.text, "html.parser")
        quote_elements = soup.select("div.quote")
        records: List[RawRecord] = []

        for idx, q_el in enumerate(quote_elements, start=1):
            try:
                record = self._parse_quote_element(q_el, url, idx)
                if record:
                    records.append(record)
            except Exception as e:
                logger.warning(f"Error parsing quote element #{idx} on {url}: {e}")
                self.errors_encountered.append({"url": url, "error": str(e)})

        # Pagination detection
        next_btn = soup.select_one("li.next a")
        next_url = None
        if next_btn and next_btn.get("href"):
            next_url = urljoin(url, next_btn["href"])

        return records, next_url

    def _parse_quote_element(self, q_el, current_url: str, idx: int) -> Optional[RawRecord]:
        """Extracts data fields from a single quote element."""
        # 1. Quote text
        text_el = q_el.select_one("span.text")
        if not text_el:
            return None
        quote_text = text_el.get_text(strip=True)

        # 2. Author
        author_el = q_el.select_one("small.author")
        author = author_el.get_text(strip=True) if author_el else None

        # 3. Tags
        tags = [tag.get_text(strip=True) for tag in q_el.select("div.tags a.tag")]

        # 4. Author 'about' URL (for additional context)
        about_link = q_el.select_one("a[href*='/author/']")
        author_url = urljoin(current_url, about_link["href"]) if about_link and about_link.get("href") else None

        # Build permalink / unique anchor for original source_url
        item_source_url = f"{current_url}#quote-{idx}"

        return RawRecord(
            source=self.SOURCE_NAME,
            source_url=item_source_url,
            data={
                "text": quote_text,
                "author": author,
                "tags": tags,
                "author_url": author_url,
                "category": None,      # Quotes do not have category taxonomies
                "description": None,
            },
        )
