"""
Integration tests for the complete ScrapingPipeline.
Tests full flow: Scraping (mocked) -> Cleaning -> Validation -> Deduplication -> CSV/JSON Export.
"""

import csv
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from config import ScraperConfig
from pipeline import ScrapingPipeline
from processing.models import RawRecord


class TestPipelineIntegration:
    """Integration test suite for the complete consolidation pipeline."""

    @pytest.fixture
    def mock_raw_data(self):
        return [
            # Book 1
            RawRecord(
                source="Books to Scrape",
                source_url="https://books.toscrape.com/catalogue/book-1/index.html",
                data={
                    "title": "A Light in the Attic",
                    "price": "£51.77",
                    "rating": ["star-rating", "Three"],
                    "availability": "In stock",
                    "category": "Poetry",
                    "description": "A delightful collection of poetry.",
                },
            ),
            # Book 2 (Duplicate with whitespace/case difference)
            RawRecord(
                source="Books to Scrape",
                source_url="https://books.toscrape.com/catalogue/book-1-dup/index.html",
                data={
                    "title": "  a light in the attic  ",
                    "price": "£51.77",
                    "rating": ["star-rating", "Three"],
                    "availability": "In stock",
                    "category": "Poetry",
                },
            ),
            # Book 3 (Invalid record - missing title)
            RawRecord(
                source="Books to Scrape",
                source_url="https://books.toscrape.com/catalogue/book-invalid/index.html",
                data={"title": "", "price": "£10.00"},
            ),
            # Quote 1
            RawRecord(
                source="Quotes to Scrape",
                source_url="https://quotes.toscrape.com/#quote-1",
                data={
                    "text": "“The world as we have created it is a process of our thinking.”",
                    "author": "Albert Einstein",
                    "tags": ["change", "thinking"],
                },
            ),
        ]

    def test_pipeline_end_to_end(self, mock_raw_data):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            out_dir = tmp_path / "output"
            logs_dir = tmp_path / "logs"

            config = ScraperConfig(
                output_dir=str(out_dir),
                logs_dir=str(logs_dir),
                dedup_action="remove",
            )
            pipeline = ScrapingPipeline(config)

            # Patch BooksScraper and QuotesScraper scrape methods
            with patch("pipeline.BooksScraper.scrape", return_value=mock_raw_data[:3]):
                with patch("pipeline.QuotesScraper.scrape", return_value=mock_raw_data[3:]):
                    summary = pipeline.run()

            # Verify funnels
            funnel = summary["pipeline_funnel_metrics"]
            assert funnel["total_records_collected"] == 4
            assert funnel["total_records_after_cleaning"] == 4
            assert funnel["records_rejected_validation"] == 1  # Book 3 rejected
            assert funnel["duplicate_records_detected"] == 1   # Book 2 duplicate
            assert funnel["final_record_count"] == 2           # Book 1 and Quote 1 survive

            # Verify CSV output
            csv_path = out_dir / "final_dataset.csv"
            assert csv_path.exists()
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = list(csv.DictReader(f))
                assert len(reader) == 2
                assert reader[0]["source"] == "Books to Scrape"
                assert reader[0]["name_or_title"] == "A Light in the Attic"
                assert float(reader[0]["price"]) == 51.77
                assert int(reader[0]["rating"]) == 3
                assert reader[1]["source"] == "Quotes to Scrape"
                assert "Albert Einstein" in reader[1]["author"]

            # Verify JSON output
            json_path = out_dir / "final_dataset.json"
            assert json_path.exists()
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                assert len(json_data) == 2

            # Verify summary report JSON
            summary_path = out_dir / "summary_report.json"
            assert summary_path.exists()
            with open(summary_path, "r", encoding="utf-8") as f:
                saved_summary = json.load(f)
                assert saved_summary["pipeline_funnel_metrics"]["final_record_count"] == 2
