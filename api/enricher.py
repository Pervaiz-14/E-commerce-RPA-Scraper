import time
from typing import Dict, List, Optional

import requests

from models.product import Product
from helpers.logger import setup_logger
from config import EXCHANGE_API_BASE

logger = setup_logger(__name__)


class Enricher:
    """
    Enricher class that provides utilities to convert product prices to a target currency.
    Uses exchangerate.host (free, no key required) by default.
    """

    def __init__(self, base_api: str = EXCHANGE_API_BASE, timeout: int = 10):
        self.base_api = base_api.rstrip("/")
        self.timeout = timeout
        self._rate_cache: Dict[str, Dict[str, float]] = {}

    def _get_rate(self, from_ccy: str, to_ccy: str) -> Optional[float]:
        # Caching based on pair
        pair = f"{from_ccy.upper()}_{to_ccy.upper()}"
        if pair in self._rate_cache:
            return self._rate_cache[pair].get("rate")
        url = f"{self.base_api}/convert"
        params = {"from": from_ccy, "to": to_ccy, "amount": 1}
        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            if data.get("success") is False:
                logger.warning("Exchange API returned unsuccessful response for %s->%s", from_ccy, to_ccy)
                return None
            rate = None
            if "result" in data and isinstance(data["result"], (int, float)):
                rate = float(data["result"])
            elif "info" in data and isinstance(data["info"], dict) and "rate" in data["info"]:
                rate = float(data["info"]["rate"])
            elif "rates" in data and isinstance(data["rates"], dict):
                rate = float(next(iter(data["rates"].values())))
            if rate is not None:
                self._rate_cache[pair] = {"rate": rate, "fetched_at": time.time()}
                return rate
            return None
        except Exception as exc:
            logger.exception("Failed to fetch exchange rate: %s", exc)
            return None

    def convert_products(
        self, products: List[Product], target_currency: str = "USD"
    ) -> List[Optional[float]]:
        """Return list of converted prices (or None) corresponding to products list."""
        converted = []
        for p in products:
            if p.price is None:
                converted.append(None)
                continue
            # If currency is missing, assume already in target
            if not p.currency:
                converted.append(float(p.price))
                continue
            # Try to map symbol to ISO code if possible (simple mapping)
            symbol = p.currency.strip()
            iso = self._symbol_to_iso(symbol)
            if not iso:
                # unknown symbol -> assume target currency
                try:
                    converted.append(float(p.price))
                except Exception:
                    converted.append(None)
                continue
            if iso.upper() == target_currency.upper():
                converted.append(float(p.price))
                continue
            rate = self._get_rate(iso, target_currency)
            if rate is None:
                converted.append(None)
                continue
            try:
                converted_price = float(p.price) * rate
                converted.append(round(converted_price, 2))
            except Exception:
                converted.append(None)
        return converted

    @staticmethod
    def _symbol_to_iso(symbol: str) -> Optional[str]:
        # Minimal mapping. Extend as needed.
        mapping = {
            "$": "USD",
            "€": "EUR",
            "£": "GBP",
            "¥": "JPY",
            "₹": "INR",
            "USD": "USD",
            "EUR": "EUR",
            "GBP": "GBP",
            "JPY": "JPY",
            "INR": "INR",
        }
        sym = symbol.replace(" ", "")
        return mapping.get(sym) or mapping.get(sym.upper())
