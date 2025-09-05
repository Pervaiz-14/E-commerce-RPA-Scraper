import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Ecommerce Product Data").strip()
TARGET_CURRENCY = os.getenv("TARGET_CURRENCY", "USD").strip().upper()
HEADLESS = os.getenv("HEADLESS", "true").lower() in ("1", "true", "yes")
DEFAULT_MAX_ITEMS = int(os.getenv("DEFAULT_MAX_ITEMS", "50"))
EXCHANGE_API_BASE = os.getenv("EXCHANGE_API_BASE", "https://api.exchangerate.host").rstrip("/")
