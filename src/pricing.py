import re
from decimal import Decimal


_GBP_PRICE_PATTERN = re.compile(
    r"^£(?P<amount>\d+(?:\.\d{1,2})?)$"
)

_CURRENCY_SYMBOLS = {
    "GBP": "£",
}


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


def format_price(
    price_minor: int,
    currency: str,
) -> str:
    if (
        not isinstance(price_minor, int)
        or isinstance(price_minor, bool)
        or price_minor < 0
    ):
        raise ValueError(
            "price_minor must be a non-negative integer."
        )

    amount = Decimal(price_minor) / Decimal(100)
    symbol = _CURRENCY_SYMBOLS.get(currency)

    if symbol is None:
        return f"{amount:.2f} {currency}"

    return f"{symbol}{amount:.2f}"
