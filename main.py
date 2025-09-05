import sys
from typing import List

from config import TARGET_CURRENCY, DEFAULT_MAX_ITEMS, HEADLESS, GOOGLE_SHEET_NAME, GOOGLE_SERVICE_ACCOUNT_JSON
from helpers.logger import setup_logger
from scraper.selenium_scraper import SeleniumScraper
from api.enricher import Enricher
from sheets.uploader import SheetsUploader
from models.product import Product

logger = setup_logger("main")


def _read_input(prompt: str, default: str | None = None) -> str:
    if default:
        sys.stdout.write(f"{prompt} [{default}]: ")
    else:
        sys.stdout.write(f"{prompt}: ")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return default or ""
    val = line.strip()
    return val if val else (default or "")


def main():
    sys.stdout.write("E-commerce RPA Scraper and Google Sheets Uploader\n")
    sys.stdout.write("------------------------------------------------\n")

    url = _read_input("Enter target listing URL (full URL)")
    if not url:
        sys.stdout.write("No URL provided. Exiting.\n")
        return

    max_items_in = _read_input("Max items to scrape", str(DEFAULT_MAX_ITEMS))
    try:
        max_items = int(max_items_in)
    except Exception:
        max_items = DEFAULT_MAX_ITEMS

    tgt_ccy = _read_input("Target currency (ISO)", TARGET_CURRENCY).upper() or TARGET_CURRENCY

    headless = HEADLESS

    # Initialize components
    scraper = SeleniumScraper(headless=headless)
    enricher = Enricher()
    if not GOOGLE_SERVICE_ACCOUNT_JSON:
        sys.stdout.write("GOOGLE_SERVICE_ACCOUNT_JSON is not configured. Set it in .env. Exiting.\n")
        return
    uploader = SheetsUploader(creds_json_path=GOOGLE_SERVICE_ACCOUNT_JSON, sheet_name=GOOGLE_SHEET_NAME)

    sys.stdout.write("Starting scrape...\n")
    products = scraper.scrape_products(url, max_items=max_items)
    sys.stdout.write(f"Scraped {len(products)} products\n")

    sys.stdout.write("Converting prices...\n")
    converted = enricher.convert_products(products, target_currency=tgt_ccy)

    sys.stdout.write("Uploading to Google Sheets...\n")
    uploader.upload_products(products, converted, target_currency=tgt_ccy)

    sys.stdout.write("Done.\n")


if __name__ == "__main__":
    main()
