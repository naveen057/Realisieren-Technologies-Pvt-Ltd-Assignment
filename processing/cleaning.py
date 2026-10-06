"""
Data Cleaning & Standardization Module.

Contains isolated, reusable functions for cleaning strings, converting prices,
standardizing ratings, normalizing URLs, and transforming raw records into
the standardized common data model.
"""

import html
import re
import unicodedata
from typing import Any, List, Optional
from urllib.parse import urljoin, urlparse

from processing.models import RawRecord, StandardRecord

# Mapping word-based ratings to numeric integers
WORD_TO_RATING = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}

# Values considered equivalent to empty / missing
MISSING_VALUES = {"", "n/a", "na", "null", "none", "nan", "nil", "undefined"}


def clean_whitespace(val: Optional[str]) -> Optional[str]:
    """
    Remove unnecessary whitespace: strips leading/trailing whitespace
    and collapses internal sequences of whitespace into a single space.
    """
    if val is None:
        return None
    cleaned = re.sub(r"\s+", " ", str(val)).strip()
    return cleaned if cleaned else None


def clean_text(val: Optional[str]) -> Optional[str]:
    """
    Standardize text:
    - HTML entity unescaping (&amp; -> &, &quot; -> ", etc.)
    - Unicode normalization (NFKC)
    - Replace curly/smart quotes with standard ASCII quotes
    - Whitespace normalization
    - Empty/null value normalization
    """
    if val is None:
        return None

    # Unescape HTML entities
    text = html.unescape(str(val))

    # Unicode normalization to decompose/recompose compatibility characters
    text = unicodedata.normalize("NFKC", text)

    # Standardize typographic quotes and apostrophes
    text = re.sub(r"[“”„‟«»]", '"', text)
    text = re.sub(r"[‘’‚‛`]", "'", text)

    # Clean whitespace
    text = clean_whitespace(text)

    if text is None:
        return None

    # Check for empty or placeholder values
    if text.lower() in MISSING_VALUES:
        return None

    return text


def clean_price(val: Any) -> Optional[float]:
    """
    Extract and convert price string to float.
    Handles currency symbols (£, $, €, Â£), trailing spaces, and commas.

    Examples:
        '£51.77' -> 51.77
        'Â£51.77' -> 51.77
        '$1,250.50' -> 1250.50
        '0.00' -> 0.0
        'Free' -> 0.0
        None -> None
    """
    if val is None:
        return None

    if isinstance(val, (int, float)):
        return round(float(val), 2)

    s = str(val).strip()
    if s.lower() in MISSING_VALUES or s == "":
        return None

    if s.lower() == "free":
        return 0.0

    # Remove commas used as thousands separators
    s = s.replace(",", "")

    # Match numeric float / integer
    match = re.search(r"(\d+(?:\.\d+)?)", s)
    if match:
        try:
            num = float(match.group(1))
            return round(num, 2)
        except (ValueError, TypeError):
            return None

    return None


def clean_rating(val: Any) -> Optional[int]:
    """
    Standardize star ratings into an integer (1 to 5).
    Accepts words ('Three', 'five'), class lists (['star-rating', 'Three']),
    or numbers ('3', 4.0, '4/5').

    Examples:
        'Three' -> 3
        ['star-rating', 'Four'] -> 4
        '5' -> 5
        '4/5' -> 4
    """
    if val is None:
        return None

    # If it's a list (e.g. HTML class list)
    if isinstance(val, (list, tuple)):
        for item in val:
            cleaned_item = str(item).strip().lower()
            if cleaned_item in WORD_TO_RATING:
                return WORD_TO_RATING[cleaned_item]
        # Try joining or checking first non-star-rating class
        val = " ".join(str(i) for i in val if str(i).lower() != "star-rating")

    s = str(val).strip().lower()

    if s in MISSING_VALUES:
        return None

    # Check word match
    for word, num in WORD_TO_RATING.items():
        if word in s:
            return num

    # Check numeric match (e.g. "4/5", "4 out of 5", "4")
    num_match = re.search(r"\b([0-5])\b", s)
    if num_match:
        try:
            return int(num_match.group(1))
        except (ValueError, TypeError):
            pass

    return None


def clean_url(url: Optional[str], base_url: Optional[str] = None) -> Optional[str]:
    """
    Normalize and validate URL:
    - Resolves relative URLs if base_url is provided
    - Strips whitespace
    - Validates scheme and domain
    """
    if url is None:
        return None

    cleaned = str(url).strip()
    if not cleaned or cleaned.lower() in MISSING_VALUES:
        return None

    if base_url:
        cleaned = urljoin(base_url, cleaned)

    parsed = urlparse(cleaned)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        return cleaned

    return None


def clean_tags(tags: Any) -> Optional[str]:
    """
    Standardize tags list or string into a clean, comma-separated string.
    Removes duplicates while preserving order.

    Examples:
        ['thinking', 'world', 'thinking'] -> 'thinking, world'
        'tag1, tag2' -> 'tag1, tag2'
    """
    if tags is None:
        return None

    raw_items: List[str] = []
    if isinstance(tags, (list, tuple)):
        raw_items = [str(t) for t in tags]
    elif isinstance(tags, str):
        raw_items = tags.split(",")
    else:
        raw_items = [str(tags)]

    seen = set()
    cleaned_items: List[str] = []
    for item in raw_items:
        c = clean_text(item)
        if c and c.lower() not in seen:
            seen.add(c.lower())
            cleaned_items.append(c)

    return ", ".join(cleaned_items) if cleaned_items else None


def clean_record(raw: RawRecord) -> StandardRecord:
    """
    Transform and clean a RawRecord into a StandardRecord according to source.
    Ensures complete isolation between scraping and transformation logic.
    """
    source = clean_text(raw.source) or "Unknown"
    source_url = clean_url(raw.source_url) or raw.source_url
    data = raw.data or {}

    if "book" in source.lower():
        title = clean_text(data.get("title") or data.get("name_or_title")) or ""
        category = clean_text(data.get("category"))
        price = clean_price(data.get("price"))
        rating = clean_rating(data.get("rating"))
        author = clean_text(data.get("author"))  # None for books unless provided
        tags = clean_tags(data.get("tags"))
        description = clean_text(data.get("description"))

        return StandardRecord(
            source=source,
            name_or_title=title,
            source_url=source_url,
            category=category,
            price=price,
            rating=rating,
            author=author,
            tags=tags,
            description=description,
            scraped_at=raw.scraped_at,
        )

    elif "quote" in source.lower():
        quote_text = clean_text(
            data.get("text") or data.get("quote") or data.get("name_or_title")
        ) or ""
        author = clean_text(data.get("author"))
        tags = clean_tags(data.get("tags"))
        category = clean_text(data.get("category"))  # Usually None or primary tag
        description = clean_text(data.get("description"))

        return StandardRecord(
            source=source,
            name_or_title=quote_text,
            source_url=source_url,
            category=category,
            price=None,     # Quotes do not have prices
            rating=None,    # Quotes do not have ratings
            author=author,
            tags=tags,
            description=description,
            scraped_at=raw.scraped_at,
        )

    else:
        # Fallback for generic sources
        return StandardRecord(
            source=source,
            name_or_title=clean_text(data.get("name_or_title") or data.get("title")) or "",
            source_url=source_url,
            category=clean_text(data.get("category")),
            price=clean_price(data.get("price")),
            rating=clean_rating(data.get("rating")),
            author=clean_text(data.get("author")),
            tags=clean_tags(data.get("tags")),
            description=clean_text(data.get("description")),
            scraped_at=raw.scraped_at,
        )
