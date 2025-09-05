from typing import List

import gspread
from gspread.exceptions import APIError

from models.product import Product
from helpers.logger import setup_logger
from config import GOOGLE_SHEET_NAME, GOOGLE_SERVICE_ACCOUNT_JSON

logger = setup_logger(__name__)


class SheetsUploader:
    """
    Simple Google Sheets uploader using gspread and a service account JSON file.
    """

    HEADER = [
        "Name",
        "Raw Price",
        "Detected Currency",
        "Parsed Price",
        "Target Currency",
        "Converted Price",
        "Rating",
        "Product URL",
    ]

    def __init__(self, creds_json_path: str = GOOGLE_SERVICE_ACCOUNT_JSON, sheet_name: str = GOOGLE_SHEET_NAME):
        if not creds_json_path:
            raise ValueError("Path to Google service account JSON must be provided")
        self.creds_path = creds_json_path
        self.sheet_name = sheet_name
        self.client = gspread.service_account(filename=self.creds_path)

    def _ensure_sheet(self):
        try:
            sh = None
            try:
                sh = self.client.open(self.sheet_name)
            except Exception:
                sh = self.client.create(self.sheet_name)
            worksheet = None
            try:
                worksheet = sh.sheet1
            except APIError:
                worksheet = sh.get_worksheet(0)
            # Ensure header
            current = worksheet.row_values(1)
            if current != self.HEADER:
                worksheet.insert_row(self.HEADER, index=1)
            return worksheet
        except Exception as exc:
            logger.exception("Failed to open or prepare spreadsheet: %s", exc)
            raise

    def upload_products(self, products: List[Product], converted_prices: List[float | None], target_currency: str):
        worksheet = self._ensure_sheet()
        rows = []
        for p, conv in zip(products, converted_prices):
            rows.append(p.as_row(target_currency, conv))
        try:
            # Append rows in batch
            worksheet.append_rows(rows, value_input_option="USER_ENTERED")
            logger.info("Uploaded %d rows to sheet '%s'", len(rows), self.sheet_name)
        except Exception:
            logger.exception("Failed to append rows, attempting row-by-row upload")
            for row in rows:
                try:
                    worksheet.append_row(row, value_input_option="USER_ENTERED")
                except Exception:
                    logger.exception("Failed to append row: %s", row)
