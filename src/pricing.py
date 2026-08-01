import re
from decimal import Decimal


_GBP_PRICE_PATTERN = re.compile(
    r"^£(?P<amount>\d+(?:\.\d{1,2})?)$"
)


def parse_price(price_text: str) -> tuple[int, str]:
    if not isinstance(price_text, str):
        raise ValueError("Price must be a string.")

    normalized_price = price_text.strip()
    match = _GBP_PRICE_PATTERN.fullmatch(normalized_price)

    if match is None:
        raise ValueError(
            f"Invalid GBP price: {price_text!r}"
        )

    amount = Decimal(match.group("amount"))
    price_minor = int(amount * 100)

    return price_minor, "GBP"