# E-commerce RPA Scraper and Google Sheets Uploader
This project scrapes product data from an e-commerce listing page using Selenium, enriches/normalizes prices via a currency conversion API, and uploads results to a Google Sheet using gspread.

Setup
1. Create and activate a Python 3.10+ virtual environment.
2. Install dependencies:
   pip install -r requirements.txt
3. Copy .env.example to .env and update values:
   - GOOGLE_SERVICE_ACCOUNT_JSON: service account JSON path for Google Sheets access.
   - GOOGLE_SHEET_NAME: spreadsheet name.
   - TARGET_CURRENCY: ISO currency code to normalize prices to (e.g., USD).
4. For Selenium, Chrome is recommended. The webdriver-manager package will install the appropriate driver automatically.
5. Run the script:
   python main.py

Usage
- The script will prompt for:
  - Target URL (listing page)
  - Maximum number of products to scrape
  - Target currency (press Enter to use default)
- It will scrape product name, price, currency symbol, numeric price, and rating (if available).
- Prices are converted to the target currency (if detected) using exchangerate.host.
- Results are uploaded to the configured Google Sheet.

Notes
- Selectors are intentionally generic. For reliable scraping, inspect the target site and provide custom CSS selectors in the code or extend the SeleniumScraper class.
- Ensure the Google service account has access to the Google Sheet (share the sheet with the service account email if necessary).
