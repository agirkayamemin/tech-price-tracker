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