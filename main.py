"""
Main CLI Entry Point for Multi-Source Web Scraping & Data Consolidation Pipeline.

Provides flexible command-line arguments to configure sources, pagination limits,
polite rate limiting, deduplication strategies, and logging levels.
"""

import argparse
import logging
import sys
from pathlib import Path

from config import ScraperConfig
from pipeline import ScrapingPipeline


def setup_logging(logs_dir: str, log_level: str = "INFO") -> None:
    """Configures dual console and file logging with UTF-8 support."""
    Path(logs_dir).mkdir(parents=True, exist_ok=True)
    log_file = Path(logs_dir) / "scraper.log"

    level = getattr(logging, log_level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler with UTF-8
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments for the scraper."""
    parser = argparse.ArgumentParser(
        description="Multi-Source Web Scraping & Data Consolidation Pipeline"
    )

    parser.add_argument(
        "--sources",
        nargs="+",
        choices=["books", "quotes"],
        default=["books", "quotes"],
        help="Specify which sources to scrape (default: books quotes)",
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=3,
        help="Maximum pages to scrape per source. Pass 0 or omit to scrape all pages (default: 3).",
    )

    parser.add_argument(
        "--all-pages",
        action="store_true",
        help="Scrape all available pages until pagination ends (overrides --max-pages).",
    )

    parser.add_argument(
        "--rate-limit",
        type=float,
        default=0.2,
        help="Delay in seconds between HTTP requests for polite scraping (default: 0.2).",
    )

    parser.add_argument(
        "--fetch-details",
        action="store_true",
        default=True,
        help="Visit individual book pages to extract category and description (default: True).",
    )

    parser.add_argument(
        "--no-details",
        action="store_false",
        dest="fetch_details",
        help="Skip visiting individual book pages to optimize speed.",
    )

    parser.add_argument(
        "--dedup-action",
        choices=["remove", "flag"],
        default="remove",
        help="Action for detected duplicates: 'remove' (drop) or 'flag' (mark in output).",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Directory where output files will be written (default: output).",
    )

    parser.add_argument(
        "--logs-dir",
        type=str,
        default="logs",
        help="Directory where log files will be written (default: logs).",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity level (default: INFO).",
    )

    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_arguments()

    # Configure logging
    setup_logging(args.logs_dir, args.log_level)
    logger = logging.getLogger("main")

    max_pages = None if args.all_pages or args.max_pages == 0 else args.max_pages

    config = ScraperConfig(
        max_pages=max_pages,
        rate_limit_delay=args.rate_limit,
        fetch_book_details=args.fetch_details,
        output_dir=args.output_dir,
        logs_dir=args.logs_dir,
        dedup_action=args.dedup_action,
        log_level=args.log_level,
    )

    logger.info("Initializing Scraping Pipeline with settings:")
    logger.info(f"  - Sources: {args.sources}")
    logger.info(f"  - Max Pages: {'ALL' if max_pages is None else max_pages}")
    logger.info(f"  - Rate Limit Delay: {config.rate_limit_delay}s")
    logger.info(f"  - Fetch Book Details: {config.fetch_book_details}")
    logger.info(f"  - Deduplication Strategy: {config.dedup_action}")
    logger.info(f"  - Output Directory: {config.output_dir}")

    pipeline = ScrapingPipeline(config)
    summary = pipeline.run(sources=args.sources)

    print("\n" + "=" * 60)
    print("           SCRAPING EXECUTION SUMMARY REPORT")
    print("=" * 60)
    funnel = summary["pipeline_funnel_metrics"]
    print(f"Total Raw Records Collected:    {funnel['total_records_collected']}")
    print(f"Total Records After Cleaning:   {funnel['total_records_after_cleaning']}")
    print(f"Records Rejected by Validation: {funnel['records_rejected_validation']}")
    print(f"Duplicates Detected:            {funnel['duplicate_records_detected']}")
    print(f"Final Consolidated Records:     {funnel['final_record_count']}")
    print(f"Total Execution Time:           {summary['pipeline_metadata']['execution_time_seconds']}s")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
