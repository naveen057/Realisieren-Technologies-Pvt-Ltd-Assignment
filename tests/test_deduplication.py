"""
Unit Tests for Duplicate Detection and Deduplication Module.
"""

import pytest

from processing.deduplication import Deduplicator, normalize_for_comparison, generate_dedup_key
from processing.models import StandardRecord


class TestDeduplication:
    """Test suite for duplicate detection strategies."""

    def test_normalize_for_comparison(self):
        # Case, whitespace, and punctuation variations
        t1 = "Example Book Title"
        t2 = "  Example Book Title "
        t3 = "EXAMPLE BOOK TITLE"
        t4 = "Example Book Title!"
        t5 = "“Example Book Title”"

        norm1 = normalize_for_comparison(t1)
        norm2 = normalize_for_comparison(t2)
        norm3 = normalize_for_comparison(t3)
        norm4 = normalize_for_comparison(t4)
        norm5 = normalize_for_comparison(t5)

        assert norm1 == "example book title"
        assert norm1 == norm2 == norm3 == norm4 == norm5

    def test_dedup_action_remove(self):
        deduplicator = Deduplicator(action="remove")

        records = [
            StandardRecord(
                source="Books to Scrape",
                name_or_title="Example Book Title",
                source_url="https://books.toscrape.com/catalogue/book-1/index.html",
                price=10.0,
            ),
            StandardRecord(
                source="Books to Scrape",
                name_or_title="  EXAMPLE BOOK TITLE  ",
                source_url="https://books.toscrape.com/catalogue/book-1-dup/index.html",
                price=10.0,
            ),
            StandardRecord(
                source="Books to Scrape",
                name_or_title="Different Book",
                source_url="https://books.toscrape.com/catalogue/book-2/index.html",
                price=15.0,
            ),
        ]

        cleaned, audit = deduplicator.process(records)
        assert len(cleaned) == 2
        assert len(audit) == 1
        assert cleaned[0].name_or_title == "Example Book Title"
        assert cleaned[1].name_or_title == "Different Book"
        assert audit[0].action_taken == "removed"
        assert audit[0].duplicate_url == "https://books.toscrape.com/catalogue/book-1-dup/index.html"

    def test_dedup_action_flag(self):
        deduplicator = Deduplicator(action="flag")

        records = [
            StandardRecord(
                source="Books to Scrape",
                name_or_title="The Great Gatsby",
                source_url="https://books.toscrape.com/catalogue/gatsby-1/index.html",
            ),
            StandardRecord(
                source="Books to Scrape",
                name_or_title="the great gatsby",
                source_url="https://books.toscrape.com/catalogue/gatsby-2/index.html",
            ),
        ]

        cleaned, audit = deduplicator.process(records)
        assert len(cleaned) == 2
        assert len(audit) == 1
        assert cleaned[0].is_duplicate is False
        assert cleaned[1].is_duplicate is True
        assert cleaned[1].duplicate_of == "https://books.toscrape.com/catalogue/gatsby-1/index.html"
        assert audit[0].action_taken == "flagged"

    def test_quotes_composite_deduplication(self):
        deduplicator = Deduplicator(action="remove")

        records = [
            StandardRecord(
                source="Quotes to Scrape",
                name_or_title="Life is what happens when you are busy making other plans.",
                author="John Lennon",
                source_url="https://quotes.toscrape.com/#q1",
            ),
            StandardRecord(
                source="Quotes to Scrape",
                name_or_title="  “Life is what happens when you are busy making other plans.” ",
                author="  JOHN LENNON ",
                source_url="https://quotes.toscrape.com/#q2",
            ),
            StandardRecord(
                source="Quotes to Scrape",
                name_or_title="Life is what happens when you are busy making other plans.",
                author="Anonymous",  # Different author
                source_url="https://quotes.toscrape.com/#q3",
            ),
        ]

        cleaned, audit = deduplicator.process(records)
        assert len(cleaned) == 2
        assert len(audit) == 1
        assert cleaned[0].author == "John Lennon"
        assert cleaned[1].author == "Anonymous"
