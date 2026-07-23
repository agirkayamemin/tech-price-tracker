import sqlite3
from unittest.mock import patch, Mock

from src.scraper import scrape


def create_test_database(test_db):
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


def test_scrape(tmp_path):
    fake_html = """
    <html>
        <body>
            <article class="product_pod">
                <h3>
                    <a title="Test Book">Test Book</a>
                </h3>

                <p class="price_color">£10.00</p>
            </article>
        </body>
    </html>
    """

    test_db = tmp_path / "test.db"

    create_test_database(test_db)

    mock_response = Mock()
    mock_response.text = fake_html

    with patch("src.scraper.requests.get", return_value=mock_response):
        scrape(test_db)

    connection = sqlite3.connect(test_db)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE name = ?",
        ("Test Book",)
    )

    product = cursor.fetchone()

    assert product is not None
    assert product[1] == "Test Book"
    assert product[2] == "£10.00"

    cursor.execute(
        "SELECT * FROM price_history WHERE product_id = ?",
        (product[0],)
    )

    history = cursor.fetchone()

    assert history is not None
    assert history[1] == product[0]
    assert history[2] == "£10.00"
    assert history[3] is not None

    connection.close()


def test_scrape_price_change(tmp_path):
    test_db = tmp_path / "test.db"

    create_test_database(test_db)

    first_html = """
    <html>
        <body>
            <article class="product_pod">
                <h3>
                    <a title="Test Book">Test Book</a>
                </h3>

                <p class="price_color">£10.00</p>
            </article>
        </body>
    </html>
    """

    second_html = """
    <html>
        <body>
            <article class="product_pod">
                <h3>
                    <a title="Test Book">Test Book</a>
                </h3>

                <p class="price_color">£20.00</p>
            </article>
        </body>
    </html>
    """

    first_response = Mock()
    first_response.text = first_html

    second_response = Mock()
    second_response.text = second_html

    with patch(
        "src.scraper.requests.get",
        return_value=first_response
    ):
        scrape(test_db)

    with patch(
        "src.scraper.requests.get",
        return_value=second_response
    ):
        scrape(test_db)

    connection = sqlite3.connect(test_db)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE name = ?",
        ("Test Book",)
    )

    product = cursor.fetchone()

    assert product is not None
    assert product[2] == "£20.00"

    cursor.execute(
        "SELECT * FROM price_history WHERE product_id = ?",
        (product[0],)
    )

    history = cursor.fetchall()

    assert len(history) == 2
    assert history[0][2] == "£10.00"
    assert history[1][2] == "£20.00"

    connection.close()