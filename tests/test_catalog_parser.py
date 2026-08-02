from pathlib import Path

from src.catalog_parser import (
    find_next_page,
    parse_products,
)
from src.models import ProductData


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_parse_products_returns_normalized_products():
    html = (
        FIXTURES_DIR / "catalog_page_1.html"
    ).read_text(encoding="utf-8")

    products = parse_products(
        html,
        page_url="https://books.toscrape.com/",
    )

    assert products == [
        ProductData(
            source="books.toscrape.com",
            product_url=(
                "https://books.toscrape.com/"
                "catalogue/a-light-in-the-attic_1000/index.html"
            ),
            name="A Light in the Attic",
            price_minor=5177,
            currency="GBP",
        )
    ]

def test_parse_products_skips_malformed_products(
    caplog,
):
    html = (
        FIXTURES_DIR / "malformed_product.html"
    ).read_text(encoding="utf-8")

    products = parse_products(
        html,
        page_url="https://books.toscrape.com/",
    )

    assert products == []
    assert caplog.text.count(
        "Skipping malformed product"
    ) == 2

def test_find_next_page_returns_absolute_url():
    html = (
        FIXTURES_DIR / "catalog_page_1.html"
    ).read_text(encoding="utf-8")

    next_page_url = find_next_page(
        html,
        page_url="https://books.toscrape.com/",
    )

    assert next_page_url == (
        "https://books.toscrape.com/"
        "catalogue/page-2.html"
    )

def test_parse_products_preserves_special_characters():
    html = (
        FIXTURES_DIR / "catalog_page_2.html"
    ).read_text(encoding="utf-8")

    products = parse_products(
        html,
        page_url=(
            "https://books.toscrape.com/"
            "catalogue/page-2.html"
        ),
    )

    assert products[0].name == (
        "Shakespeare's Sonnets & Stories"
    )


def test_find_next_page_returns_none_on_last_page():
    html = (
        FIXTURES_DIR / "catalog_page_2.html"
    ).read_text(encoding="utf-8")

    next_page_url = find_next_page(
        html,
        page_url=(
            "https://books.toscrape.com/"
            "catalogue/page-2.html"
        ),
    )

    assert next_page_url is None