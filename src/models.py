from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProductData:
    source: str
    product_url: str
    name: str
    price_minor: int
    currency: str