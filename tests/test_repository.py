from src.database import (
    connect_db,
    list_price_history,
    list_products,
    open_connection,
    upsert_product,
)
from src.models import ProductData
from datetime import datetime, timedelta

import sqlite3
from datetime import datetime, timedelta

import pytest

def test_upsert_product_creates_product_and_history(
    tmp_path,
 ):
    test_db = tmp_path / "test.db"
    connect_db(test_db)

    product = ProductData(
        source="books.toscrape.com",
        product_url="https://example.com/book",
        name="Test Book",
        price_minor=1000,
        currency="GBP",
    )

    status = upsert_product(
        product,
        test_db,
        checked_at="2026-08-02T10:00:00+00:00",
    )

    with open_connection(test_db) as connection:
        stored_product = connection.execute(
            """
            SELECT
                id,
                source,
                product_url,
                name,
                current_price_minor,
                currency
            FROM products
            """
        ).fetchone()

        stored_history = connection.execute(
            """
            SELECT
                product_id,
                price_minor,
                currency,
                checked_at
            FROM price_history
            """
        ).fetchone()

    assert status == "created"
    assert stored_product[1:] == (
        "books.toscrape.com",
        "https://example.com/book",
        "Test Book",
        1000,
        "GBP",
    )
    assert stored_history == (
        stored_product[0],
        1000,
        "GBP",
        "2026-08-02T10:00:00+00:00",
    )

def test_upsert_product_does_not_duplicate_unchanged_product(
    tmp_path,
):
    test_db = tmp_path / "test.db"
    connect_db(test_db)

    product = ProductData(
        source="books.toscrape.com",
        product_url="https://example.com/book",
        name="Test Book",
        price_minor=1000,
        currency="GBP",
    )

    first_status = upsert_product(
        product,
        test_db,
        checked_at="2026-08-02T10:00:00+00:00",
    )
    second_status = upsert_product(
        product,
        test_db,
        checked_at="2026-08-02T11:00:00+00:00",
    )

    with open_connection(test_db) as connection:
        product_count = connection.execute(
            "SELECT COUNT(*) FROM products"
        ).fetchone()[0]

        history_count = connection.execute(
            "SELECT COUNT(*) FROM price_history"
        ).fetchone()[0]

    assert first_status == "created"
    assert second_status == "unchanged"
    assert product_count == 1
    assert history_count == 1


def test_upsert_product_updates_changed_price_and_history(
    tmp_path,
):
    test_db = tmp_path / "test.db"
    connect_db(test_db)

    original_product = ProductData(
        source="books.toscrape.com",
        product_url="https://example.com/book",
        name="Test Book",
        price_minor=1000,
        currency="GBP",
    )
    changed_product = ProductData(
        source="books.toscrape.com",
        product_url="https://example.com/book",
        name="Updated Book Name",
        price_minor=1500,
        currency="GBP",
    )

    upsert_product(
        original_product,
        test_db,
        checked_at="2026-08-02T10:00:00+00:00",
    )
    status = upsert_product(
        changed_product,
        test_db,
        checked_at="2026-08-02T11:00:00+00:00",
    )

    with open_connection(test_db) as connection:
        stored_product = connection.execute(
            """
            SELECT
                name,
                current_price_minor,
                currency
            FROM products
            """
        ).fetchone()

        history = connection.execute(
            """
            SELECT
                price_minor,
                currency,
                checked_at
            FROM price_history
            ORDER BY id
            """
        ).fetchall()

    assert status == "updated"
    assert stored_product == (
        "Updated Book Name",
        1500,
        "GBP",
    )
    assert history == [
        (
            1000,
            "GBP",
            "2026-08-02T10:00:00+00:00",
        ),
        (
            1500,
            "GBP",
            "2026-08-02T11:00:00+00:00",
        ),
    ]


def test_upsert_product_updates_name_without_new_history(
    tmp_path,
):
    test_db = tmp_path / "test.db"
    connect_db(test_db)

    original_product = ProductData(
        source="books.toscrape.com",
        product_url="https://example.com/book",
        name="Original Name",
        price_minor=1000,
        currency="GBP",
    )
    renamed_product = ProductData(
        source="books.toscrape.com",
        product_url="https://example.com/book",
        name="Updated Name",
        price_minor=1000,
        currency="GBP",
    )

    upsert_product(
        original_product,
        test_db,
        checked_at="2026-08-02T10:00:00+00:00",
    )
    status = upsert_product(
        renamed_product,
        test_db,
        checked_at="2026-08-02T11:00:00+00:00",
    )

    with open_connection(test_db) as connection:
        stored_name = connection.execute(
            "SELECT name FROM products"
        ).fetchone()[0]

        history_count = connection.execute(
            "SELECT COUNT(*) FROM price_history"
        ).fetchone()[0]

    assert status == "unchanged"
    assert stored_name == "Updated Name"
    assert history_count == 1


def test_upsert_product_uses_utc_timestamp_by_default(
    tmp_path,
):
    test_db = tmp_path / "test.db"
    connect_db(test_db)

    product = ProductData(
        source="books.toscrape.com",
        product_url="https://example.com/book",
        name="Test Book",
        price_minor=1000,
        currency="GBP",
    )

    status = upsert_product(
        product,
        test_db,
    )

    with open_connection(test_db) as connection:
        checked_at = connection.execute(
            """
            SELECT checked_at
            FROM price_history
            """
        ).fetchone()[0]

    parsed_timestamp = datetime.fromisoformat(
        checked_at
    )

    assert status == "created"
    assert parsed_timestamp.utcoffset() == timedelta(0)


def test_price_update_rolls_back_when_history_fails(
    tmp_path,
):
    test_db = tmp_path / "test.db"
    connect_db(test_db)

    original_product = ProductData(
        source="books.toscrape.com",
        product_url="https://example.com/book",
        name="Test Book",
        price_minor=1000,
        currency="GBP",
    )
    changed_product = ProductData(
        source="books.toscrape.com",
        product_url="https://example.com/book",
        name="Test Book",
        price_minor=1500,
        currency="GBP",
    )

    upsert_product(
        original_product,
        test_db,
        checked_at="2026-08-02T10:00:00+00:00",
    )

    with open_connection(test_db) as connection:
        connection.execute(
            """
            CREATE TRIGGER fail_history_insert
            BEFORE INSERT ON price_history
            BEGIN
                SELECT RAISE(
                    ABORT,
                    'forced history failure'
                );
            END
            """
        )

    with pytest.raises(
        sqlite3.IntegrityError,
        match="forced history failure",
    ):
        upsert_product(
            changed_product,
            test_db,
            checked_at="2026-08-02T11:00:00+00:00",
        )

    with open_connection(test_db) as connection:
        current_price = connection.execute(
            """
            SELECT current_price_minor
            FROM products
            """
        ).fetchone()[0]

        history_count = connection.execute(
            "SELECT COUNT(*) FROM price_history"
        ).fetchone()[0]

    assert current_price == 1000
    assert history_count == 1


def test_list_products_returns_sorted_v2_records(
    tmp_path,
):
    test_db = tmp_path / "test.db"
    connect_db(test_db)

    product_b = ProductData(
        source="books.toscrape.com",
        product_url="https://example.com/book-b",
        name="B Book",
        price_minor=2000,
        currency="GBP",
    )
    product_a = ProductData(
        source="books.toscrape.com",
        product_url="https://example.com/book-a",
        name="A Book",
        price_minor=1000,
        currency="GBP",
    )

    upsert_product(product_b, test_db)
    upsert_product(product_a, test_db)

    products = list_products(test_db)

    assert len(products) == 2
    assert products[0][1:] == (
        "books.toscrape.com",
        "https://example.com/book-a",
        "A Book",
        1000,
        "GBP",
    )
    assert products[1][1:] == (
        "books.toscrape.com",
        "https://example.com/book-b",
        "B Book",
        2000,
        "GBP",
    )


def test_list_price_history_returns_numeric_history(
    tmp_path,
):
    test_db = tmp_path / "test.db"
    connect_db(test_db)

    original_product = ProductData(
        source="books.toscrape.com",
        product_url="https://example.com/book",
        name="Test Book",
        price_minor=1000,
        currency="GBP",
    )
    changed_product = ProductData(
        source="books.toscrape.com",
        product_url="https://example.com/book",
        name="Test Book",
        price_minor=1500,
        currency="GBP",
    )

    upsert_product(
        original_product,
        test_db,
        checked_at="2026-08-02T10:00:00+00:00",
    )
    upsert_product(
        changed_product,
        test_db,
        checked_at="2026-08-02T11:00:00+00:00",
    )

    product_id = list_products(test_db)[0][0]
    history = list_price_history(
        product_id,
        test_db,
    )

    assert history == [
        (
            1000,
            "GBP",
            "2026-08-02T10:00:00+00:00",
        ),
        (
            1500,
            "GBP",
            "2026-08-02T11:00:00+00:00",
        ),
    ]