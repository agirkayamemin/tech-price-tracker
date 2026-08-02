from dataclasses import FrozenInstanceError

import pytest

from src.models import ProductData


def test_product_data_stores_normalized_values():
    product = ProductData(
        source="books.toscrape.com",
        product_url=(
            "https://books.toscrape.com/"
            "catalogue/a-light-in-the-attic_1000/index.html"
        ),
        name="A Light in the Attic",
        price_minor=5177,
        currency="GBP",
    )

    assert product.source == "books.toscrape.com"
    assert product.name == "A Light in the Attic"
    assert product.price_minor == 5177
    assert product.currency == "GBP"


def test_product_data_is_immutable():
    product = ProductData(
        source="books.toscrape.com",
        product_url="https://example.com/product",
        name="Test Book",
        price_minor=1000,
        currency="GBP",
    )

    with pytest.raises(FrozenInstanceError):
        product.name = "Changed Name"