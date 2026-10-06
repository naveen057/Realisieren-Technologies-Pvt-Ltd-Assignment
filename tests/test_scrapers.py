"""
Unit Tests for BooksScraper and QuotesScraper parsing logic.
Uses mocked HTML fixtures to ensure deterministic, network-independent test runs.
"""

from bs4 import BeautifulSoup

from config import ScraperConfig
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

SAMPLE_BOOK_POD_HTML = """
<article class="product_pod">
    <div class="image_container">
        <a href="catalogue/a-light-in-the-attic_1000/index.html">
            <img src="media/cache/test.jpg" alt="A Light in the Attic" class="thumbnail"/>
        </a>
    </div>
    <p class="star-rating Three">
        <i class="icon-star"></i>
    </p>
    <h3>
        <a href="catalogue/a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light in the ...</a>
    </h3>
    <div class="product_price">
        <p class="price_color">£51.77</p>
        <p class="instock availability">
            <i class="icon-ok"></i>
            In stock
        </p>
    </div>
</article>
"""

SAMPLE_QUOTE_HTML = """
<div class="quote" itemscope="" itemtype="http://schema.org/CreativeWork">
    <span class="text" itemprop="text">“The world as we have created it is a process of our thinking.”</span>
    <span>by <small class="author" itemprop="author">Albert Einstein</small>
    <a href="/author/Albert-Einstein">(about)</a>
    </span>
    <div class="tags">
        Tags:
        <a class="tag" href="/tag/change/">change</a>
        <a class="tag" href="/tag/thinking/">thinking</a>
    </div>
</div>
"""


class TestScrapers:
    """Test suite for HTML element parsing."""

    def test_books_pod_parsing(self):
        config = ScraperConfig(fetch_book_details=False)
        scraper = BooksScraper(config)

        soup = BeautifulSoup(SAMPLE_BOOK_POD_HTML, "html.parser")
        pod = soup.select_one("article.product_pod")

        record = scraper._parse_book_pod(pod, "https://books.toscrape.com/index.html")

        assert record is not None
        assert record.source == "Books to Scrape"
        assert record.source_url == "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
        assert record.data["title"] == "A Light in the Attic"
        assert record.data["price"] == "£51.77"
        assert "Three" in record.data["rating"]
        assert "In stock" in record.data["availability"]

    def test_quotes_element_parsing(self):
        config = ScraperConfig()
        scraper = QuotesScraper(config)

        soup = BeautifulSoup(SAMPLE_QUOTE_HTML, "html.parser")
        q_el = soup.select_one("div.quote")

        record = scraper._parse_quote_element(q_el, "https://quotes.toscrape.com/page/1/", 1)

        assert record is not None
        assert record.source == "Quotes to Scrape"
        assert "Albert Einstein" in record.data["author"]
        assert "thinking" in record.data["text"]
        assert "change" in record.data["tags"]
        assert "thinking" in record.data["tags"]

    def test_books_pagination_link_extraction(self):
        page_html = """
        <html>
            <body>
                <ul class="pager">
                    <li class="next"><a href="page-2.html">next</a></li>
                </ul>
            </body>
        </html>
        """
        soup = BeautifulSoup(page_html, "html.parser")
        next_btn = soup.select_one("li.next a")
        assert next_btn is not None
        from urllib.parse import urljoin
        next_url = urljoin("https://books.toscrape.com/catalogue/page-1.html", next_btn["href"])
        assert next_url == "https://books.toscrape.com/catalogue/page-2.html"

    def test_quotes_pagination_link_extraction(self):
        page_html = """
        <html>
            <body>
                <ul class="pager">
                    <li class="next"><a href="/page/2/">Next</a></li>
                </ul>
            </body>
        </html>
        """
        soup = BeautifulSoup(page_html, "html.parser")
        next_btn = soup.select_one("li.next a")
        assert next_btn is not None
        from urllib.parse import urljoin
        next_url = urljoin("https://quotes.toscrape.com/page/1/", next_btn["href"])
        assert next_url == "https://quotes.toscrape.com/page/2/"
