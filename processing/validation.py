"""
Data Validation Module.

Validates standardized records against defined schema rules and business logic,
separating valid records from rejected ones and collecting validation failure reasons.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Set, Tuple
from urllib.parse import urlparse

from processing.models import StandardRecord

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Represents the validation result for an individual record."""

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Add a fatal validation error that causes record rejection."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add a non-fatal warning that retains the record."""
        self.warnings.append(message)


class Validator:
    """Validator for verifying standardized dataset records."""

    KNOWN_SOURCES: Set[str] = {"Books to Scrape", "Quotes to Scrape"}

    def __init__(self, allowed_sources: Optional[Set[str]] = None):
        self.allowed_sources = allowed_sources or self.KNOWN_SOURCES

    def validate(self, record: StandardRecord) -> ValidationResult:
        """
        Validate a single StandardRecord.

        Rules:
        1. source: Must be recognizable.
        2. name_or_title: Mandatory non-empty string.
        3. source_url: Mandatory valid HTTP/HTTPS URL.
        4. price: If present, must be numeric float >= 0.0.
        5. rating: If present, must be integer between 1 and 5.
        6. scraped_at: Must be parseable ISO-8601 timestamp.
        """
        result = ValidationResult(is_valid=True)

        # 1. Source validation
        if not record.source or not record.source.strip():
            result.add_error("Source is required and cannot be empty.")
        elif record.source not in self.allowed_sources:
            result.add_warning(
                f"Source '{record.source}' is not in known sources {self.allowed_sources}."
            )

        # 2. Name or Title validation (Mandatory)
        if not record.name_or_title or not record.name_or_title.strip():
            result.add_error("Mandatory field 'name_or_title' is missing or empty.")
        elif len(record.name_or_title.strip()) < 1:
            result.add_error("Field 'name_or_title' is too short.")

        # 3. Source URL validation (Mandatory)
        if not record.source_url or not record.source_url.strip():
            result.add_error("Mandatory field 'source_url' is missing or empty.")
        else:
            parsed = urlparse(record.source_url.strip())
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                result.add_error(
                    f"Invalid URL structure in 'source_url': {record.source_url}"
                )

        # 4. Price validation
        if record.price is not None:
            if not isinstance(record.price, (int, float)):
                result.add_error(f"Price must be numeric, got {type(record.price).__name__}.")
            elif record.price < 0:
                result.add_error(f"Price cannot be negative: {record.price}.")
            elif record.price > 100000:
                result.add_warning(f"Price appears unusually high: {record.price}.")

        # 5. Rating validation
        if record.rating is not None:
            if not isinstance(record.rating, int):
                result.add_error(f"Rating must be an integer, got {type(record.rating).__name__}.")
            elif not (1 <= record.rating <= 5):
                result.add_error(f"Rating must be between 1 and 5, got {record.rating}.")

        # 6. Source-specific field checks
        if "quote" in record.source.lower():
            if not record.author:
                result.add_warning("Quote record is missing an author name.")

        # 7. Timestamp validation
        if record.scraped_at:
            try:
                datetime.fromisoformat(record.scraped_at)
            except (ValueError, TypeError):
                result.add_warning(f"scraped_at is not a standard ISO timestamp: {record.scraped_at}")

        return result

    def validate_batch(
        self, records: List[StandardRecord]
    ) -> Tuple[List[StandardRecord], List[Tuple[StandardRecord, ValidationResult]]]:
        """
        Validate a collection of records.
        Returns:
            (valid_records, rejected_records_with_reasons)
        """
        valid_records: List[StandardRecord] = []
        rejected: List[Tuple[StandardRecord, ValidationResult]] = []

        for record in records:
            res = self.validate(record)
            if res.is_valid:
                valid_records.append(record)
            else:
                rejected.append((record, res))
                logger.warning(
                    f"Validation failed for record '{record.name_or_title[:30]}...': "
                    f"{'; '.join(res.errors)}"
                )

        return valid_records, rejected


def validate_record(record: StandardRecord) -> ValidationResult:
    """Convenience helper to validate a single record."""
    validator = Validator()
    return validator.validate(record)
