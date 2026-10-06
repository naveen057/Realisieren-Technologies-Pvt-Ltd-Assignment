"""
Base Web Scraper Module.

Provides an abstract foundation for web scrapers with integrated session management,
exponential backoff retries, polite rate limiting, and robust error handling.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import ScraperConfig
from processing.models import RawRecord

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base class providing shared networking, retry logic,
    rate-limiting, and error handling for web scrapers.
    """

    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        self.session = self._create_session()
        self.pages_scraped: int = 0
        self.items_scraped: int = 0
        self.errors_encountered: List[Dict[str, Any]] = []

    def _create_session(self) -> requests.Session:
        """Create and configure a robust requests session with retries."""
        session = requests.Session()
        session.headers.update({
            "User-Agent": self.config.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })

        # Exponential backoff retry strategy for transient errors
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def fetch_url(self, url: str) -> Optional[requests.Response]:
        """
        Fetch a URL with polite rate limiting and comprehensive error handling.
        Returns response object or None if the request failed after retries.
        """
        if self.config.rate_limit_delay > 0:
            time.sleep(self.config.rate_limit_delay)

        try:
            logger.debug(f"Fetching URL: {url}")
            response = self.session.get(url, timeout=self.config.request_timeout)

            # Ensure response uses UTF-8 if charset not specified or misdetected
            if response.encoding is None or response.encoding.lower() == "iso-8859-1":
                response.encoding = "utf-8"

            if response.status_code == 200:
                return response
            elif response.status_code == 404:
                logger.warning(f"URL returned 404 Not Found: {url}")
                return None
            else:
                msg = f"HTTP {response.status_code} for URL: {url}"
                logger.warning(msg)
                self.errors_encountered.append({"url": url, "error": msg})
                return None

        except requests.exceptions.Timeout as e:
            msg = f"Timeout fetching {url}: {e}"
            logger.error(msg)
            self.errors_encountered.append({"url": url, "error": msg})
            return None
        except requests.exceptions.ConnectionError as e:
            msg = f"Connection error for {url}: {e}"
            logger.error(msg)
            self.errors_encountered.append({"url": url, "error": msg})
            return None
        except requests.exceptions.RequestException as e:
            msg = f"Request exception for {url}: {e}"
            logger.error(msg)
            self.errors_encountered.append({"url": url, "error": msg})
            return None

    @abstractmethod
    def scrape(self) -> List[RawRecord]:
        """Execute complete scraping process and return collected raw records."""
        pass

    @abstractmethod
    def scrape_page(self, url: str) -> Tuple[List[RawRecord], Optional[str]]:
        """
        Parse a single page.
        Returns:
            (records_found, next_page_url)
        """
        pass

    def close(self) -> None:
        """Close HTTP session."""
        self.session.close()

    def __enter__(self) -> "BaseScraper":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
