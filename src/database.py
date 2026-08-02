import sqlite3
from datetime import datetime

from src.config import DATABASE_PATH

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
                "Legacy database schema detected. "
                "Delete the local database and "
                "run scan again."
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

def save_product(name, price, db_path=DATABASE_PATH):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO products (name, price) VALUES (?, ?)",
            (name, price)
        )

        product_id = cursor.lastrowid

        connection.commit()
    except sqlite3.IntegrityError:
        product_id = None

    connection.close()

    return product_id

def get_product(name, db_path=DATABASE_PATH):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE name = ?",
        (name,)
    )

    product = cursor.fetchone()

    connection.close()

    return product

def update_price(name, price, db_path=DATABASE_PATH):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE products SET price = ? WHERE name = ?",
        (price, name)
    )

    connection.commit()
    connection.close()

def save_price_history(product_id, price, db_path=DATABASE_PATH):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO price_history (product_id, price, checked_at)
        VALUES (?, ?, ?)
        """,
        (
            product_id,
            price,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    connection.commit()
    connection.close()

def get_price_history(product_id, db_path=DATABASE_PATH):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT price, checked_at
        FROM price_history
        WHERE product_id = ?
        ORDER BY checked_at ASC
        """,
        (product_id,)
    )

    history = cursor.fetchall()

    connection.close()

    return history

def get_all_products(db_path=DATABASE_PATH):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, price
        FROM products
        ORDER BY name ASC
        """
    )

    products = cursor.fetchall()

    connection.close()

    return products

