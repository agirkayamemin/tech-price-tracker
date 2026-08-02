import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.models import ProductData
from src.pricing import parse_price


BOOKS_SOURCE = "books.toscrape.com"

logger = logging.getLogger(__name__)


def _parse_product(
    product_element,
    page_url: str,
) -> ProductData:
    link = product_element.select_one("h3 a")
    price_element = product_element.select_one(
        "p.price_color"
    )

    if link is None or price_element is None:
        raise ValueError(
            "Product link or price is missing."
        )

    name = link.get("title")
    product_href = link.get("href")

    if not isinstance(name, str) or not name.strip():
        raise ValueError("Product name is missing.")

    if (
        not isinstance(product_href, str)
        or not product_href.strip()
    ):
        raise ValueError("Product URL is missing.")

    price_minor, currency = parse_price(
        price_element.get_text(strip=True)
    )

    return ProductData(
        source=BOOKS_SOURCE,
        product_url=urljoin(page_url, product_href),
        name=name.strip(),
        price_minor=price_minor,
        currency=currency,
    )


def parse_products(
    html: str,
    page_url: str,
) -> list[ProductData]:
    soup = BeautifulSoup(html, "html.parser")
    products = []

    for product_element in soup.select(
        "article.product_pod"
    ):
        try:
            product = _parse_product(
                product_element,
                page_url,
            )
        except ValueError as error:
            logger.warning(
                "Skipping malformed product: %s",
                error,
            )
            continue

        products.append(product)

    return products
    

def find_next_page(
    html: str,
    page_url: str,
) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one("li.next a")

    if next_link is None:
        return None

    next_href = next_link.get("href")

    if (
        not isinstance(next_href, str)
        or not next_href.strip()
    ):
        return None

    return urljoin(page_url, next_href)