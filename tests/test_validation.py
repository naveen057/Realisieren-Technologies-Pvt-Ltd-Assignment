"""
Unit Tests for Data Validation Module.
"""

import pytest

from processing.models import StandardRecord
from processing.validation import Validator, validate_record


class TestValidation:
    """Test suite for Validator and record validation rules."""

    @pytest.fixture
    def validator(self):
        return Validator()

    def test_valid_book_record(self, validator):
        rec = StandardRecord(
            source="Books to Scrape",
            name_or_title="A Light in the Attic",
            source_url="https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
            category="Poetry",
            price=51.77,
            rating=3,
        )
        res = validator.validate(rec)
        assert res.is_valid is True
        assert len(res.errors) == 0

    def test_valid_quote_record(self, validator):
        rec = StandardRecord(
            source="Quotes to Scrape",
            name_or_title='"The world is what we make of it."',
            source_url="https://quotes.toscrape.com/#quote-1",
            author="Albert Einstein",
            tags="world, life",
        )
        res = validator.validate(rec)
        assert res.is_valid is True
        assert len(res.errors) == 0

    def test_missing_name_or_title_fails(self, validator):
        rec = StandardRecord(
            source="Books to Scrape",
            name_or_title="",
            source_url="https://books.toscrape.com/catalogue/book_1/index.html",
        )
        res = validator.validate(rec)
        assert res.is_valid is False
        assert any("name_or_title" in err for err in res.errors)

    def test_invalid_source_url_fails(self, validator):
        rec = StandardRecord(
            source="Books to Scrape",
            name_or_title="Valid Title",
            source_url="invalid-url-without-scheme",
        )
        res = validator.validate(rec)
        assert res.is_valid is False
        assert any("source_url" in err for err in res.errors)

    def test_negative_price_fails(self, validator):
        rec = StandardRecord(
            source="Books to Scrape",
            name_or_title="Discount Book",
            source_url="https://books.toscrape.com/catalogue/discount/index.html",
            price=-10.50,
        )
        res = validator.validate(rec)
        assert res.is_valid is False
        assert any("Price cannot be negative" in err for err in res.errors)

    def test_rating_out_of_range_fails(self, validator):
        rec = StandardRecord(
            source="Books to Scrape",
            name_or_title="Super Book",
            source_url="https://books.toscrape.com/catalogue/super/index.html",
            rating=6,
        )
        res = validator.validate(rec)
        assert res.is_valid is False
        assert any("Rating must be between 1 and 5" in err for err in res.errors)

    def test_batch_validation_partitions_properly(self, validator):
        valid = StandardRecord(
            source="Books to Scrape",
            name_or_title="Good Book",
            source_url="https://books.toscrape.com/catalogue/good/index.html",
            price=19.99,
            rating=4,
        )
        invalid = StandardRecord(
            source="Books to Scrape",
            name_or_title="",
            source_url="https://books.toscrape.com/catalogue/bad/index.html",
        )
        valid_list, rejected_list = validator.validate_batch([valid, invalid])
        assert len(valid_list) == 1
        assert len(rejected_list) == 1
        assert valid_list[0].name_or_title == "Good Book"
        assert rejected_list[0][0].source_url == "https://books.toscrape.com/catalogue/bad/index.html"
