"""
Data models for the scraping and consolidation pipeline.

Defines schemas for raw extracted data and the standardized output model.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class RawRecord:
    """Represents uncleaned, raw scraped data extracted from a source website."""

    source: str
    source_url: str
    data: Dict[str, Any]
    scraped_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class StandardRecord:
    """
    Standardized schema representing a consolidated record across all sources.

    Complies with the assessment's suggested schema:
    source, name_or_title, category, price, rating, author, tags, description, source_url, scraped_at
    """

    source: str
    name_or_title: str
    source_url: str
    category: Optional[str] = None
    price: Optional[float] = None
    rating: Optional[int] = None
    author: Optional[str] = None
    tags: Optional[str] = None
    description: Optional[str] = None
    scraped_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Duplicate tracking metadata
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None

    def to_dict(self, include_dup_metadata: bool = False) -> Dict[str, Any]:
        """Convert record to dictionary, optionally including duplicate metadata."""
        d = {
            "source": self.source,
            "name_or_title": self.name_or_title,
            "category": self.category,
            "price": self.price,
            "rating": self.rating,
            "author": self.author,
            "tags": self.tags,
            "description": self.description,
            "source_url": self.source_url,
            "scraped_at": self.scraped_at,
        }
        if include_dup_metadata:
            d["is_duplicate"] = self.is_duplicate
            d["duplicate_of"] = self.duplicate_of
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StandardRecord":
        """Reconstruct a StandardRecord from a dictionary."""
        return cls(
            source=data.get("source", ""),
            name_or_title=data.get("name_or_title", ""),
            source_url=data.get("source_url", ""),
            category=data.get("category"),
            price=data.get("price"),
            rating=data.get("rating"),
            author=data.get("author"),
            tags=data.get("tags"),
            description=data.get("description"),
            scraped_at=data.get("scraped_at") or datetime.now(timezone.utc).isoformat(),
            is_duplicate=bool(data.get("is_duplicate", False)),
            duplicate_of=data.get("duplicate_of"),
        )
