import sqlite3


def connect_db():
    connection = sqlite3.connect("data/products.db")

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            price TEXT
)
    """)

    connection.commit()
    connection.close()

    print("Veritabanı hazır.")

def save_product(name, price):
    connection = sqlite3.connect("data/products.db")
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO products (name, price) VALUES (?, ?)",
            (name, price)
        )
        connection.commit()
    except sqlite3.IntegrityError:
        pass

    connection.close()

def get_product(name):
    connection = sqlite3.connect("data/products.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE name = ?",
        (name,)
    )

    product = cursor.fetchone()

    connection.close()

    return product

def update_price(name, price):
    connection = sqlite3.connect("data/products.db")
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE products SET price = ? WHERE name = ?",
        (price, name)
    )

    connection.commit()
    connection.close()