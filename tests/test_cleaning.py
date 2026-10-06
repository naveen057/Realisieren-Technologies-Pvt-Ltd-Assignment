"""
Unit Tests for Data Cleaning and Normalization Functions.
"""

import pytest

from processing.cleaning import (
    clean_whitespace,
    clean_text,
    clean_price,
    clean_rating,
    clean_url,
    clean_tags,
    clean_record,
)
from processing.models import RawRecord


class TestCleaningFunctions:
    """Test suite for isolated cleaning functions."""

    def test_clean_whitespace(self):
        assert clean_whitespace("  hello   world  ") == "hello world"
        assert clean_whitespace("line1\n\tline2\r\nline3") == "line1 line2 line3"
        assert clean_whitespace("") is None
        assert clean_whitespace("   ") is None
        assert clean_whitespace(None) is None

    def test_clean_text_unicode_and_quotes(self):
        # Curly quotes
        assert clean_text('“Hello” and ‘World’') == '"Hello" and \'World\''
        # HTML entities
        assert clean_text("Books &amp; More &quot;Gifts&quot;") == 'Books & More "Gifts"'
        # Placeholder / missing values
        assert clean_text("N/A") is None
        assert clean_text("null") is None
        assert clean_text("  none  ") is None
        assert clean_text(None) is None

    def test_clean_price(self):
        # UK Pound currency
        assert clean_price("£51.77") == 51.77
        assert clean_price("Â£51.77") == 51.77
        # US Dollar with comma
        assert clean_price("$1,234.56") == 1234.56
        # Free
        assert clean_price("Free") == 0.0
        # Numeric inputs
        assert clean_price(29.99) == 29.99
        assert clean_price(45) == 45.0
        # Invalid / missing
        assert clean_price("N/A") is None
        assert clean_price("unavailable") is None
        assert clean_price(None) is None

    def test_clean_rating(self):
        # Word-based ratings
        assert clean_rating("One") == 1
        assert clean_rating("Two") == 2
        assert clean_rating("Three") == 3
        assert clean_rating("Four") == 4
        assert clean_rating("Five") == 5
        # From HTML class list
        assert clean_rating(["star-rating", "Three"]) == 3
        assert clean_rating(["star-rating", "Five"]) == 5
        # Numeric / fractional strings
        assert clean_rating("4") == 4
        assert clean_rating("4/5") == 4
        assert clean_rating(5) == 5
        # Invalid / missing
        assert clean_rating(None) is None
        assert clean_rating("No Rating") is None

    def test_clean_url(self):
        # Relative URL resolution
        base = "https://books.toscrape.com/catalogue/page-2.html"
        assert clean_url("page-3.html", base) == "https://books.toscrape.com/catalogue/page-3.html"
        assert clean_url("a-light-in-the-attic_1000/index.html", "https://books.toscrape.com/catalogue/") == (
            "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
        )
        # Invalid URLs
        assert clean_url("javascript:void(0)") is None
        assert clean_url("") is None
        assert clean_url(None) is None

    def test_clean_tags(self):
        # List of tags
        raw = ["change", "world", "change", "  deep-thoughts  "]
        assert clean_tags(raw) == "change, world, deep-thoughts"
        # String with commas
        assert clean_tags("tag1, tag2, tag1") == "tag1, tag2"
        # Empty
        assert clean_tags([]) is None
        assert clean_tags(None) is None

    def test_clean_record_books(self):
        raw = RawRecord(
            source="Books to Scrape",
            source_url="https://books.toscrape.com/catalogue/book_1/index.html",
            data={
                "title": "  A Light in the Attic  ",
                "price": "£51.77",
                "rating": ["star-rating", "Three"],
                "category": "Poetry",
                "description": "It's a poetry book.",
            },
        )
        cleaned = clean_record(raw)
        assert cleaned.source == "Books to Scrape"
        assert cleaned.name_or_title == "A Light in the Attic"
        assert cleaned.price == 51.77
        assert cleaned.rating == 3
        assert cleaned.category == "Poetry"
        assert cleaned.author is None
        assert cleaned.tags is None

    def test_clean_record_quotes(self):
        raw = RawRecord(
            source="Quotes to Scrape",
            source_url="https://quotes.toscrape.com/#quote-1",
            data={
                "text": "“The world is what we make of it.”",
                "author": " Albert Einstein ",
                "tags": ["world", "life", "world"],
            },
        )
        cleaned = clean_record(raw)
        assert cleaned.source == "Quotes to Scrape"
        assert cleaned.name_or_title == '"The world is what we make of it."'
        assert cleaned.author == "Albert Einstein"
        assert cleaned.tags == "world, life"
        assert cleaned.price is None
        assert cleaned.rating is None
