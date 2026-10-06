"""
Duplicate Detection and Deduplication Module.

Implements fuzzy and normalized duplicate detection across records.
Handles variations in whitespace, capitalization, and punctuation.
Supports both filtering duplicates or flagging them in-place.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from processing.models import StandardRecord

logger = logging.getLogger(__name__)


def normalize_for_comparison(text: Optional[str]) -> str:
    """
    Normalizes a string for robust duplicate matching:
    - Lowercase
    - Strip leading and trailing whitespace
    - Collapse consecutive whitespace into single space
    - Remove punctuation and symbols so formatting variations match
      (e.g., 'Example Book Title!', '  example   book  title  ', 'EXAMPLE BOOK TITLE')

    Examples:
        'Example Book Title' -> 'example book title'
        '  Example Book Title! ' -> 'example book title'
        '“Don\'t cry because it\'s over”' -> 'dont cry because its over'
    """
    if not text:
        return ""

    s = text.lower().strip()
    # Remove apostrophes without adding spaces to keep words together (don't -> dont)
    s = re.sub(r"['’`]", "", s)
    # Replace punctuation and non-alphanumeric characters with spaces
    s = re.sub(r"[^\w\s]", " ", s)
    # Collapse multiple whitespaces
    s = re.sub(r"\s+", " ", s).strip()
    return s


def generate_dedup_key(record: StandardRecord) -> str:
    """
    Generates a deterministic composite deduplication key based on source-specific logic.

    - Books: Combines normalized title.
    - Quotes: Combines normalized author and normalized quote text.
    - Generic: Combines source and normalized name_or_title.
    """
    source_lower = record.source.lower()
    norm_name = normalize_for_comparison(record.name_or_title)

    if "book" in source_lower:
        # A book is uniquely identified by its canonical normalized title
        return f"books::{norm_name}"

    elif "quote" in source_lower:
        # A quote is uniquely identified by its author + quote text
        norm_author = normalize_for_comparison(record.author or "unknown")
        # Use first 150 characters of quote text for stability
        quote_snippet = norm_name[:150]
        return f"quotes::{norm_author}::{quote_snippet}"

    else:
        return f"{source_lower}::{norm_name}"


@dataclass
class DuplicateAuditRecord:
    """Audit entry documenting a detected duplicate."""
    duplicate_key: str
    source: str
    name_or_title: str
    source_url: str
    original_url: str
    action_taken: str

    @property
    def duplicate_url(self) -> str:
        """Alias for source_url for audit reporting clarity."""
        return self.source_url


class Deduplicator:
    """
    Identifies and resolves duplicate records across datasets.
    """

    def __init__(self, action: str = "remove"):
        """
        Args:
            action: 'remove' to exclude duplicates from output,
                    'flag' to retain records with is_duplicate=True.
        """
        if action not in ("remove", "flag"):
            raise ValueError(f"Invalid dedup action '{action}'. Choose 'remove' or 'flag'.")
        self.action = action
        self.seen_keys: Dict[str, StandardRecord] = {}
        self.duplicates_detected: List[DuplicateAuditRecord] = []

    def process(
        self, records: List[StandardRecord]
    ) -> Tuple[List[StandardRecord], List[DuplicateAuditRecord]]:
        """
        Processes a list of StandardRecords, identifying duplicates.

        Returns:
            (processed_records, duplicate_audit_log)
        """
        output_records: List[StandardRecord] = []
        self.seen_keys.clear()
        self.duplicates_detected.clear()

        for record in records:
            key = generate_dedup_key(record)

            if key in self.seen_keys:
                original = self.seen_keys[key]
                record.is_duplicate = True
                record.duplicate_of = original.source_url

                audit_entry = DuplicateAuditRecord(
                    duplicate_key=key,
                    source=record.source,
                    name_or_title=record.name_or_title,
                    source_url=record.source_url,
                    original_url=original.source_url,
                    action_taken="removed" if self.action == "remove" else "flagged",
                )
                self.duplicates_detected.append(audit_entry)

                logger.info(
                    f"Duplicate detected: '{record.name_or_title[:40]}' "
                    f"matches original from {original.source_url} (Action: {self.action})"
                )

                if self.action == "flag":
                    # Retain the record with flag set
                    output_records.append(record)
                # If action == "remove", skip adding to output_records
            else:
                self.seen_keys[key] = record
                record.is_duplicate = False
                record.duplicate_of = None
                output_records.append(record)

        return output_records, self.duplicates_detected

    @property
    def duplicate_count(self) -> int:
        """Total number of duplicates detected during processing."""
        return len(self.duplicates_detected)
