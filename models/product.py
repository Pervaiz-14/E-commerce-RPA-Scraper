from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    name: str
    raw_price: str
    price: Optional[float]
    currency: Optional[str]
    rating: Optional[float]
    url: Optional[str] = None

    def as_row(self, target_currency: str, converted_price: float | None):
        return [
            self.name,
            self.raw_price,
            self.currency or "",
            self.price if self.price is not None else "",
            target_currency,
            converted_price if converted_price is not None else "",
            self.rating if self.rating is not None else "",
            self.url or "",
        ]
