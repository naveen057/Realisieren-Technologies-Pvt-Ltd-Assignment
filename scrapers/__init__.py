"""
Web Scrapers Package.

Contains modular scrapers for Books to Scrape and Quotes to Scrape,
built upon an abstract BaseScraper.
"""

from scrapers.base_scraper import BaseScraper
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

__all__ = ["BaseScraper", "BooksScraper", "QuotesScraper"]
