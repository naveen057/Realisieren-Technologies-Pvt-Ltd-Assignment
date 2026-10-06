"""
Data Consolidation Pipeline Module.

Orchestrates the entire end-to-end workflow:
Scraping -> Cleaning -> Validation -> Deduplication -> Consolidation -> Output Generation.
"""

import csv
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import ScraperConfig
from processing.cleaning import clean_record
from processing.deduplication import Deduplicator
from processing.models import RawRecord, StandardRecord
from processing.validation import Validator
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

logger = logging.getLogger(__name__)


class ScrapingPipeline:
    """
    End-to-end pipeline coordinating multi-source scraping, cleaning,
    validation, deduplication, and export.
    """

    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        self.config.ensure_directories()
        self.validator = Validator()
        self.deduplicator = Deduplicator(action=self.config.dedup_action)

    def run(self, sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Executes the full data collection and consolidation pipeline.

        Args:
            sources: List of sources to scrape ('books', 'quotes', or both). Defaults to both.

        Returns:
            summary_report: Comprehensive metrics and execution report.
        """
        start_time = time.time()
        logger.info("==================================================")
        logger.info("STARTING MULTI-SOURCE SCRAPING & CONSOLIDATION")
        logger.info("==================================================")

        selected_sources = [s.lower() for s in (sources or ["books", "quotes"])]

        # ----------------------------------------------------
        # Step 1: Web Scraping
        # ----------------------------------------------------
        raw_records: List[RawRecord] = []
        raw_counts_by_source: Dict[str, int] = {}
        pages_scraped_by_source: Dict[str, int] = {}
        errors_by_source: Dict[str, List[Dict[str, Any]]] = {}

        if "books" in selected_sources:
            logger.info("Initializing Books to Scrape scraper...")
            with BooksScraper(self.config) as books_scraper:
                b_records = books_scraper.scrape()
                raw_records.extend(b_records)
                raw_counts_by_source[books_scraper.SOURCE_NAME] = len(b_records)
                pages_scraped_by_source[books_scraper.SOURCE_NAME] = books_scraper.pages_scraped
                errors_by_source[books_scraper.SOURCE_NAME] = books_scraper.errors_encountered

        if "quotes" in selected_sources:
            logger.info("Initializing Quotes to Scrape scraper...")
            with QuotesScraper(self.config) as quotes_scraper:
                q_records = quotes_scraper.scrape()
                raw_records.extend(q_records)
                raw_counts_by_source[quotes_scraper.SOURCE_NAME] = len(q_records)
                pages_scraped_by_source[quotes_scraper.SOURCE_NAME] = quotes_scraper.pages_scraped
                errors_by_source[quotes_scraper.SOURCE_NAME] = quotes_scraper.errors_encountered

        logger.info(
            f"Stage 1 Complete: Total Raw Records Collected = {len(raw_records)} "
            f"({raw_counts_by_source})"
        )

        # ----------------------------------------------------
        # Step 2: Cleaning & Standardization
        # ----------------------------------------------------
        logger.info("Stage 2: Cleaning and normalizing data...")
        cleaned_records: List[StandardRecord] = []
        for raw in raw_records:
            try:
                std_record = clean_record(raw)
                cleaned_records.append(std_record)
            except Exception as e:
                logger.error(f"Error cleaning raw record from {raw.source_url}: {e}")

        logger.info(f"Stage 2 Complete: Cleaned Records = {len(cleaned_records)}")

        # ----------------------------------------------------
        # Step 3: Validation
        # ----------------------------------------------------
        logger.info("Stage 3: Validating records against schema rules...")
        valid_records, rejected_tuples = self.validator.validate_batch(cleaned_records)

        rejected_details = [
            {
                "source": r.source,
                "name_or_title": r.name_or_title,
                "source_url": r.source_url,
                "errors": res.errors,
            }
            for r, res in rejected_tuples
        ]
        logger.info(
            f"Stage 3 Complete: Valid Records = {len(valid_records)}, "
            f"Rejected = {len(rejected_tuples)}"
        )

        # ----------------------------------------------------
        # Step 4: Duplicate Detection & Resolution
        # ----------------------------------------------------
        logger.info(f"Stage 4: Running deduplication (strategy: {self.config.dedup_action})...")
        final_records, duplicates_audit = self.deduplicator.process(valid_records)

        logger.info(
            f"Stage 4 Complete: Duplicates Detected = {len(duplicates_audit)}, "
            f"Final Consolidated Records = {len(final_records)}"
        )

        # ----------------------------------------------------
        # Step 5: Export Final Dataset
        # ----------------------------------------------------
        logger.info("Stage 5: Writing consolidated output datasets...")
        self._export_datasets(final_records)

        # ----------------------------------------------------
        # Step 6: Summary Report Generation
        # ----------------------------------------------------
        elapsed_seconds = round(time.time() - start_time, 2)
        summary_report = self._build_summary_report(
            raw_counts_by_source=raw_counts_by_source,
            pages_scraped=pages_scraped_by_source,
            total_raw=len(raw_records),
            total_cleaned=len(cleaned_records),
            valid_count=len(valid_records),
            rejected_details=rejected_details,
            duplicates_audit=duplicates_audit,
            final_records=final_records,
            elapsed_seconds=elapsed_seconds,
            errors_by_source=errors_by_source,
        )

        self._export_summary(summary_report)

        logger.info("==================================================")
        logger.info(f"PIPELINE COMPLETED IN {elapsed_seconds}s")
        logger.info(f"Final dataset exported to: {self.config.output_path / self.config.dataset_filename}")
        logger.info(f"Summary report exported to: {self.config.output_path / self.config.summary_filename}")
        logger.info("==================================================")

        return summary_report

    def _export_datasets(self, records: List[StandardRecord]) -> None:
        """Exports consolidated dataset to CSV and JSON."""
        output_dir = self.config.output_path
        csv_path = output_dir / self.config.dataset_filename
        json_path = output_dir / "final_dataset.json"

        fieldnames = [
            "source",
            "name_or_title",
            "category",
            "price",
            "rating",
            "author",
            "tags",
            "description",
            "source_url",
            "scraped_at",
        ]
        if self.config.dedup_action == "flag":
            fieldnames.extend(["is_duplicate", "duplicate_of"])

        # Write CSV with UTF-8 encoding
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow(record.to_dict(include_dup_metadata=(self.config.dedup_action == "flag")))

        # Write JSON if configured
        if "json" in self.config.export_formats:
            with open(json_path, mode="w", encoding="utf-8") as f:
                json.dump(
                    [r.to_dict(include_dup_metadata=True) for r in records],
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

    def _build_summary_report(
        self,
        raw_counts_by_source: Dict[str, int],
        pages_scraped: Dict[str, int],
        total_raw: int,
        total_cleaned: int,
        valid_count: int,
        rejected_details: List[Dict[str, Any]],
        duplicates_audit: List[Any],
        final_records: List[StandardRecord],
        elapsed_seconds: float,
        errors_by_source: Dict[str, List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Constructs a comprehensive, structured metrics report."""
        final_by_source: Dict[str, int] = {}
        for r in final_records:
            final_by_source[r.source] = final_by_source.get(r.source, 0) + 1

        # Calculate completeness metrics across standardized fields
        completeness = {}
        fields_to_check = [
            "name_or_title", "category", "price", "rating",
            "author", "tags", "description", "source_url"
        ]
        total_final = len(final_records)
        if total_final > 0:
            for f in fields_to_check:
                present = sum(1 for r in final_records if getattr(r, f) is not None)
                completeness[f] = f"{round((present / total_final) * 100, 1)}%"

        return {
            "pipeline_metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "execution_time_seconds": elapsed_seconds,
                "deduplication_strategy": self.config.dedup_action,
                "rate_limit_delay_seconds": self.config.rate_limit_delay,
                "max_pages_limit": self.config.max_pages,
            },
            "source_metrics": {
                "pages_scraped": pages_scraped,
                "raw_records_collected": raw_counts_by_source,
                "final_records_by_source": final_by_source,
            },
            "pipeline_funnel_metrics": {
                "total_records_collected": total_raw,
                "total_records_after_cleaning": total_cleaned,
                "records_rejected_validation": len(rejected_details),
                "duplicate_records_detected": len(duplicates_audit),
                "final_record_count": len(final_records),
            },
            "field_completeness_percentages": completeness,
            "validation_failures": rejected_details,
            "duplicates_detected_audit": [
                {
                    "source": d.source,
                    "name_or_title": d.name_or_title,
                    "duplicate_url": d.source_url,
                    "matched_original_url": d.original_url,
                    "action_taken": d.action_taken,
                }
                for d in duplicates_audit
            ],
            "network_errors_encountered": errors_by_source,
        }

    def _export_summary(self, summary_report: Dict[str, Any]) -> None:
        """Writes summary report to JSON."""
        summary_path = self.config.output_path / self.config.summary_filename
        with open(summary_path, mode="w", encoding="utf-8") as f:
            json.dump(summary_report, f, indent=2, ensure_ascii=False)
