import sqlite3

import pytest

from src.database import (
    LegacyDatabaseError,
    connect_db,
    open_connection,
)

def test_connect_db_creates_v2_products_table(
    tmp_path,
):
    test_db = tmp_path / "test.db"

    connect_db(test_db)

    with sqlite3.connect(test_db) as connection:
        schema_version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()[0]

        columns = connection.execute(
            "PRAGMA table_info(products)"
        ).fetchall()

    column_names = [
        column[1]
        for column in columns
    ]

    assert schema_version == 2
    assert column_names == [
        "id",
        "source",
        "product_url",
        "name",
        "current_price_minor",
        "currency",
    ]


def test_v2_schema_creates_history_relationship(
    tmp_path,
):
    test_db = tmp_path / "test.db"

    connect_db(test_db)

    with sqlite3.connect(test_db) as connection:
        columns = connection.execute(
            "PRAGMA table_info(price_history)"
        ).fetchall()

        foreign_key = connection.execute(
            "PRAGMA foreign_key_list(price_history)"
        ).fetchone()

        indexes = connection.execute(
            "PRAGMA index_list(price_history)"
        ).fetchall()

    column_names = [
        column[1]
        for column in columns
    ]
    index_names = {
        index[1]
        for index in indexes
    }

    assert column_names == [
        "id",
        "product_id",
        "price_minor",
        "currency",
        "checked_at",
    ]
    assert foreign_key[2] == "products"
    assert foreign_key[3] == "product_id"
    assert foreign_key[4] == "id"
    assert foreign_key[6] == "CASCADE"
    assert (
        "idx_price_history_product_id"
        in index_names
    )

def test_connect_db_rejects_legacy_schema(
    tmp_path,
):
    test_db = tmp_path / "legacy.db"

    with sqlite3.connect(test_db) as connection:
        connection.execute(
            """
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                price TEXT
            )
            """
        )

    with pytest.raises(
        LegacyDatabaseError,
        match="Eski veritabanı şeması",
    ):
        connect_db(test_db)

    with sqlite3.connect(test_db) as connection:
        schema_version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()[0]

    assert schema_version == 0


def test_open_connection_enables_foreign_keys(
    tmp_path,
):
    test_db = tmp_path / "test.db"

    connection = open_connection(test_db)

    try:
        foreign_keys_enabled = connection.execute(
            "PRAGMA foreign_keys"
        ).fetchone()[0]
    finally:
        connection.close()

    assert foreign_keys_enabled == 1


def test_foreign_key_rejects_unknown_product(
    tmp_path,
):
    test_db = tmp_path / "test.db"
    connect_db(test_db)

    with open_connection(test_db) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO price_history (
                    product_id,
                    price_minor,
                    currency,
                    checked_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    999,
                    1000,
                    "GBP",
                    "2026-08-02T10:00:00+00:00",
                ),
            )


def test_deleting_product_cascades_history(
    tmp_path,
):
    test_db = tmp_path / "test.db"
    connect_db(test_db)

    with open_connection(test_db) as connection:
        cursor = connection.execute(
            """
            INSERT INTO products (
                source,
                product_url,
                name,
                current_price_minor,
                currency
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "books.toscrape.com",
                "https://example.com/book",
                "Test Book",
                1000,
                "GBP",
            ),
        )
        product_id = cursor.lastrowid

        connection.execute(
            """
            INSERT INTO price_history (
                product_id,
                price_minor,
                currency,
                checked_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                product_id,
                1000,
                "GBP",
                "2026-08-02T10:00:00+00:00",
            ),
        )

        connection.execute(
            "DELETE FROM products WHERE id = ?",
            (product_id,),
        )

        history_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM price_history
            WHERE product_id = ?
            """,
            (product_id,),
        ).fetchone()[0]

    assert history_count == 0
