import re
import time
from typing import List, Optional

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from models.product import Product
from helpers.logger import setup_logger
logger = setup_logger(__name__)


class SeleniumScraper:
    """
    Generic Selenium-based scraper for product listing pages.
    Usage:
        scraper = SeleniumScraper(headless=True)
        products = scraper.scrape_products(url, max_items=20)
    Notes:
        - Selectors are intentionally generic. Adjust selectors to target site structure for best results.
    """

    DEFAULT_PRODUCT_SELECTOR = ".product, .product-item, .productCard, .listing-item"
    DEFAULT_TITLE_SELECTOR = ".product-title, .title, h2, .name, a.product-name"
    DEFAULT_PRICE_SELECTOR = ".price, .product-price, .amount"
    DEFAULT_RATING_SELECTOR = ".rating, .stars, .review-count"

    PRICE_RE = re.compile(r"([^\d.,]*)([\d,]+(?:\.\d+)?)")

    def __init__(self, headless: bool = True, window_size: str = "1920,1080"):
        self.headless = headless
        self.window_size = window_size
        self.driver = None

    def _init_driver(self):
        try:
            options = Options()
            if self.headless:
                # Compatible headless option for modern Chrome
                options.add_argument("--headless=new")
            options.add_argument(f"--window-size={self.window_size}")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            self.driver = webdriver.Chrome(options=options)
        except WebDriverException as exc:
            logger.exception("Failed to initialize Selenium WebDriver: %s", exc)
            raise

    def _parse_price(self, text: str) -> tuple[Optional[float], Optional[str]]:
        if not text:
            return None, None
        text = text.strip()
        match = self.PRICE_RE.search(text.replace("\u00A0", " "))
        if not match:
            # Fallback: extract numbers
            digits = re.findall(r"[\d,]+(?:\.\d+)?", text)
            if not digits:
                return None, None
            num = digits[0].replace(",", "")
            try:
                return float(num), None
            except ValueError:
                return None, None
        symbol = match.group(1).strip()
        numtext = match.group(2).replace(",", "")
        try:
            return float(numtext), symbol if symbol else None
        except ValueError:
            return None, symbol

    def _safe_text(self, el) -> str:
        return el.get_text(" ", strip=True) if el else ""

    def scrape_products(
        self,
        url: str,
        max_items: int = 50,
        product_selector: str | None = None,
        title_selector: str | None = None,
        price_selector: str | None = None,
        rating_selector: str | None = None,
        wait_seconds: float = 2.0,
    ) -> List[Product]:
        product_selector = product_selector or self.DEFAULT_PRODUCT_SELECTOR
        title_selector = title_selector or self.DEFAULT_TITLE_SELECTOR
        price_selector = price_selector or self.DEFAULT_PRICE_SELECTOR
        rating_selector = rating_selector or self.DEFAULT_RATING_SELECTOR

        self._init_driver()
        try:
            logger.info("Opening URL: %s", url)
            self.driver.get(url)
            # Basic wait for JS-rendered content
            time.sleep(wait_seconds)
            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            items = soup.select(product_selector)
            logger.info("Found %d product-like elements (selector=%s)", len(items), product_selector)

            products = []
            for i, item in enumerate(items):
                if i >= max_items:
                    break
                title_el = item.select_one(title_selector)
                price_el = item.select_one(price_selector)
                rating_el = item.select_one(rating_selector)
                link_el = item.select_one("a")

                name = self._safe_text(title_el) or self._safe_text(item.select_one("h2, .title"))
                raw_price = self._safe_text(price_el)
                price_val, currency_symbol = self._parse_price(raw_price)
                rating_text = self._safe_text(rating_el)
                rating = None
                if rating_text:
                    try:
                        rating = float(re.findall(r"[\d.]+", rating_text)[0])
                    except Exception:
                        rating = None
                url_link = None
                if link_el and link_el.has_attr("href"):
                    url_link = link_el["href"].strip()

                product = Product(
                    name=name or "UNKNOWN",
                    raw_price=raw_price or "",
                    price=price_val,
                    currency=currency_symbol,
                    rating=rating,
                    url=url_link,
                )
                logger.debug("Scraped product: %s", product)
                products.append(product)
            return products
        finally:
            try:
                self.driver.quit()
            except Exception:
                pass
