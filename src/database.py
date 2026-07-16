import sqlite3
from config import DATABASE_PATH, URL
from datetime import datetime


def connect_db():
    connection = sqlite3.connect(DATABASE_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            price TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            price TEXT,
            checked_at TEXT,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)

    connection.commit()
    connection.close()

    print("Veritabanı hazır.")

def save_product(name, price):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO products (name, price) VALUES (?, ?)",
        (name, price)
    )

    product_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return product_id

def get_product(name):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE name = ?",
        (name,)
    )

    product = cursor.fetchone()

    connection.close()

    return product

def update_price(name, price):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE products SET price = ? WHERE name = ?",
        (price, name)
    )

    connection.commit()
    connection.close()

def save_price_history(product_id, price):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO price_history (product_id, price, checked_at)
        VALUES (?, ?, ?)
        """,
        (product_id, price, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )

    connection.commit()
    connection.close()