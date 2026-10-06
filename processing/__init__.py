"""
Data Processing Package.

Contains modules for data models, cleaning, validation, and deduplication.
"""

from processing.cleaning import clean_record, clean_price, clean_rating, clean_text, clean_url, clean_tags
from processing.deduplication import Deduplicator, generate_dedup_key
from processing.models import RawRecord, StandardRecord
from processing.validation import Validator, ValidationResult, validate_record

__all__ = [
    "RawRecord",
    "StandardRecord",
    "clean_record",
    "clean_price",
    "clean_rating",
    "clean_text",
    "clean_url",
    "clean_tags",
    "Validator",
    "ValidationResult",
    "validate_record",
    "Deduplicator",
    "generate_dedup_key",
]
