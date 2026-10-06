"""
Books to Scrape Web Scraper.

Extracts book data across pages from https://books.toscrape.com/.
Handles pagination, extraction of book cards, and optional detail page enrichment
(category and description) with resilient error handling.
"""

import logging
from typing import List, Optional, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from config import ScraperConfig
from processing.models import RawRecord
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class BooksScraper(BaseScraper):
    """Scraper implementation for Books to Scrape (https://books.toscrape.com/)."""

    SOURCE_NAME = "Books to Scrape"

    def __init__(self, config: Optional[ScraperConfig] = None):
        super().__init__(config)
        self.start_url = urljoin(self.config.books_base_url, "index.html")

    def scrape(self) -> List[RawRecord]:
        """
        Executes full pagination loop for Books to Scrape.
        Stops when next page is absent or max_pages limit is reached.
        """
        records: List[RawRecord] = []
        current_url: Optional[str] = self.start_url
        page_num = 1

        logger.info(f"Starting Books scraping from: {current_url}")

        while current_url:
            if self.config.max_pages and page_num > self.config.max_pages:
                logger.info(f"Reached maximum pages limit ({self.config.max_pages}) for Books.")
                break

            logger.info(f"[Books to Scrape] Scraping Page {page_num}: {current_url}")
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
            f"Completed Books scraping: {len(records)} records from {self.pages_scraped} pages."
        )
        return records

    def scrape_page(self, url: str) -> Tuple[List[RawRecord], Optional[str]]:
        """
        Scrapes a single listing page of Books to Scrape.

        Returns:
            (records, next_page_url)
        """
        response = self.fetch_url(url)
        if not response:
            logger.error(f"Failed to fetch books listing page: {url}")
            return [], None

        soup = BeautifulSoup(response.text, "html.parser")
        pods = soup.select("article.product_pod")
        records: List[RawRecord] = []

        for pod in pods:
            try:
                record = self._parse_book_pod(pod, url)
                if record:
                    records.append(record)
            except Exception as e:
                logger.warning(f"Error parsing book pod on {url}: {e}")
                self.errors_encountered.append({"url": url, "error": str(e)})

        # Pagination detection
        next_btn = soup.select_one("li.next a")
        next_url = None
        if next_btn and next_btn.get("href"):
            next_url = urljoin(url, next_btn["href"])

        return records, next_url

    def _parse_book_pod(self, pod, current_url: str) -> Optional[RawRecord]:
        """Extracts data fields from a single product pod element."""
        # 1. Title & URL
        title_link = pod.select_one("h3 a")
        if not title_link:
            return None

        # Full title is in the 'title' attribute; fallback to inner text
        title = title_link.get("title") or title_link.get_text(strip=True)
        href = title_link.get("href", "")
        product_url = urljoin(current_url, href)

        # 2. Price
        price_el = pod.select_one(".price_color")
        price = price_el.get_text(strip=True) if price_el else None

        # 3. Rating classes (e.g. ['star-rating', 'Three'])
        rating_el = pod.select_one("p.star-rating")
        rating_classes = rating_el.get("class", []) if rating_el else []

        # 4. Availability
        avail_el = pod.select_one(".availability")
        availability = avail_el.get_text(strip=True) if avail_el else None

        # Detail enrichment (category, description)
        category = None
        description = None

        if self.config.fetch_book_details and product_url:
            category, description = self._fetch_book_details(product_url)

        return RawRecord(
            source=self.SOURCE_NAME,
            source_url=product_url,
            data={
                "title": title,
                "price": price,
                "rating": rating_classes,
                "availability": availability,
                "category": category,
                "description": description,
            },
        )

    def _fetch_book_details(self, product_url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Visits the book detail page to extract category and description.
        Fails gracefully without stopping the pipeline if page cannot be retrieved.
        """
        try:
            res = self.fetch_url(product_url)
            if not res:
                return None, None

            soup = BeautifulSoup(res.text, "html.parser")

            # Category from breadcrumb: Home > Books > [Category] > [Title]
            breadcrumbs = soup.select(".breadcrumb li a")
            category = None
            if len(breadcrumbs) >= 3:
                category = breadcrumbs[2].get_text(strip=True)

            # Product Description
            desc_heading = soup.select_one("#product_description")
            description = None
            if desc_heading:
                desc_p = desc_heading.find_next_sibling("p")
                if desc_p:
                    description = desc_p.get_text(strip=True)

            return category, description
        except Exception as e:
            logger.warning(f"Could not fetch details for {product_url}: {e}")
            return None, None
