import sqlite3
from datetime import datetime, timezone

from src.config import DATABASE_PATH
from src.models import ProductData

SCHEMA_VERSION = 2


class LegacyDatabaseError(RuntimeError):
    pass


def open_connection(
    db_path=DATABASE_PATH,
) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


def connect_db(db_path=DATABASE_PATH):
    with open_connection(db_path) as connection:
        current_version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()[0]

        existing_tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name IN (
                  'products',
                  'price_history'
              )
            """
        ).fetchall()

        if (
            existing_tables
            and current_version != SCHEMA_VERSION
        ):
            raise LegacyDatabaseError(
                "Eski veritabanı şeması algılandı. "
                "data/products.db dosyasını silin "
                "ve scan komutunu yeniden çalıştırın."
            )

        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                product_url TEXT NOT NULL,
                name TEXT NOT NULL,
                current_price_minor INTEGER NOT NULL,
                currency TEXT NOT NULL,
                UNIQUE(source, product_url)
            );

            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                price_minor INTEGER NOT NULL,
                currency TEXT NOT NULL,
                checked_at TEXT NOT NULL,
                FOREIGN KEY (product_id)
                    REFERENCES products(id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS
                idx_price_history_product_id
            ON price_history(product_id);
            """
        )

        connection.execute(
            f"PRAGMA user_version = {SCHEMA_VERSION}"
        )

    print("Veritabanı hazır.")


def upsert_product(
    product: ProductData,
    db_path=DATABASE_PATH,
    *,
    checked_at: str | None = None,
) -> str:
    if checked_at is None:
        checked_at = datetime.now(
            timezone.utc
        ).isoformat(timespec="seconds")

    with open_connection(db_path) as connection:
        existing_product = connection.execute(
            """
            SELECT
                id,
                current_price_minor,
                currency
            FROM products
            WHERE source = ?
              AND product_url = ?
            """,
            (
                product.source,
                product.product_url,
            ),
        ).fetchone()

        if existing_product is not None:
            (
                product_id,
                current_price_minor,
                current_currency,
            ) = existing_product

            price_changed = (
                current_price_minor
                != product.price_minor
                or current_currency
                != product.currency
            )

            connection.execute(
                """
                UPDATE products
                SET
                    name = ?,
                    current_price_minor = ?,
                    currency = ?
                WHERE id = ?
                """,
                (
                    product.name,
                    product.price_minor,
                    product.currency,
                    product_id,
                ),
            )

            if not price_changed:
                return "unchanged"

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
                    product.price_minor,
                    product.currency,
                    checked_at,
                ),
            )

            return "updated"

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
                product.source,
                product.product_url,
                product.name,
                product.price_minor,
                product.currency,
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
                product.price_minor,
                product.currency,
                checked_at,
            ),
        )

    return "created"


def list_products(
    db_path=DATABASE_PATH,
) -> list[tuple[int, str, str, str, int, str]]:
    with open_connection(db_path) as connection:
        products = connection.execute(
            """
            SELECT
                id,
                source,
                product_url,
                name,
                current_price_minor,
                currency
            FROM products
            ORDER BY name ASC
            """
        ).fetchall()

    return products


def list_price_history(
    product_id: int,
    db_path=DATABASE_PATH,
) -> list[tuple[int, str, str]]:
    with open_connection(db_path) as connection:
        history = connection.execute(
            """
            SELECT
                price_minor,
                currency,
                checked_at
            FROM price_history
            WHERE product_id = ?
            ORDER BY checked_at ASC, id ASC
            """,
            (product_id,),
        ).fetchall()

    return history
