import sqlite3
from src.database import (
    save_product,
    get_product,
    update_price,
    save_price_history,
    get_price_history,
    get_all_products
)

def test_save_product(tmp_path):
    test_db = tmp_path / "test.db"

    connection = sqlite3.connect(test_db)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            price TEXT
        )
    """)

    connection.commit()
    connection.close()

    product_id = save_product(
        "Test Product",
        "£10.00",
        test_db
    )

    assert product_id is not None


def test_get_product(tmp_path):
    test_db = tmp_path / "test.db"

    connection = sqlite3.connect(test_db)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            price TEXT
        )
    """)

    connection.commit()
    connection.close()

    save_product(
        "Test Product",
        "£10.00",
        test_db
    )

    product = get_product(
        "Test Product",
        test_db
    )

    assert product is not None
    assert product[1] == "Test Product"
    assert product[2] == "£10.00"

def test_duplicate_product(tmp_path):
    test_db = tmp_path / "test.db"

    connection = sqlite3.connect(test_db)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            price TEXT
        )
    """)

    connection.commit()
    connection.close()

    first_product_id = save_product(
        "Test Product",
        "£10.00",
        test_db
    )

    second_product_id = save_product(
        "Test Product",
        "£20.00",
        test_db
    )

    assert first_product_id is not None
    assert second_product_id is None

def test_update_price(tmp_path):
    test_db = tmp_path / "test.db"

    connection = sqlite3.connect(test_db)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            price TEXT
        )
    """)

    connection.commit()
    connection.close()

    save_product(
        "Test Product",
        "£10.00",
        test_db
    )

    update_price(
        "Test Product",
        "£20.00",
        test_db
    )

    product = get_product(
        "Test Product",
        test_db
    )

    assert product[2] == "£20.00"

def test_save_price_history(tmp_path):
    test_db = tmp_path / "test.db"

    connection = sqlite3.connect(test_db)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            price TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            price TEXT,
            checked_at TEXT,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)

    connection.commit()
    connection.close()

    product_id = save_product(
        "Test Product",
        "£10.00",
        test_db
    )

    save_price_history(
        product_id,
        "£10.00",
        test_db
    )

    connection = sqlite3.connect(test_db)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM price_history WHERE product_id = ?",
        (product_id,)
    )

    history = cursor.fetchone()

    connection.close()

    assert history is not None
    assert history[1] == product_id
    assert history[2] == "£10.00"
    assert history[3] is not None

def test_get_price_history(tmp_path):
    test_db = tmp_path / "test.db"

    connection = sqlite3.connect(test_db)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            price TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            price TEXT,
            checked_at TEXT,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)

    connection.commit()
    connection.close()

    product_id = save_product(
        "Test Product",
        "£10.00",
        test_db
    )

    save_price_history(
        product_id,
        "£10.00",
        test_db
    )

    save_price_history(
        product_id,
        "£20.00",
        test_db
    )

    history = get_price_history(
        product_id,
        test_db
    )

    assert len(history) == 2
    assert history[0][0] == "£10.00"
    assert history[1][0] == "£20.00"
    assert history[0][1] is not None
    assert history[1][1] is not None

def test_get_all_products(tmp_path):
    test_db = tmp_path / "test.db"

    connection = sqlite3.connect(test_db)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            price TEXT
        )
    """)

    connection.commit()
    connection.close()

    save_product(
        "Product A",
        "£10.00",
        test_db
    )

    save_product(
        "Product B",
        "£20.00",
        test_db
    )

    products = get_all_products(test_db)

    assert len(products) == 2
    assert products[0][1] == "Product A"
    assert products[0][2] == "£10.00"
    assert products[1][1] == "Product B"
    assert products[1][2] == "£20.00"