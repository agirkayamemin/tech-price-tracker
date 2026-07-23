import requests
from bs4 import BeautifulSoup
from src.logger import logger

from src.config import URL
from src.database import (
    get_product,
    save_product,
    update_price,
    save_price_history,
)

def scrape(database_path=None):
    if database_path is None:
        from src.config import DATABASE_PATH
        database_path = DATABASE_PATH

    logger.info("Scan started.")
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        response.encoding = "utf-8"

    except requests.RequestException as e:
        print("\n❌ Web sitesine erişilemedi.")
        print(f"Detay: {e}")
        logger.error(f"Request failed: {e}")
        return
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    books = soup.find_all("article", class_="product_pod")

    new_products = 0
    updated_products = 0

    for book in books:
        name = book.find("h3").find("a")["title"]
        price = book.find("p", class_="price_color").text
        product = get_product(name, database_path)

        if product is None:
            product_id = save_product(name, price, database_path)
            save_price_history(product_id, price, database_path)

            new_products += 1
            print(f"Yeni ürün: {name}")
            logger.info(f"New product added: {name}")

        else:
            old_price = product[2]

            if old_price != price:
                update_price(name, price, database_path)
                save_price_history(product[0], price, database_path)

                updated_products += 1

                print(f"Fiyat değişti: {name}")
                logger.info(f"Price updated: {name} ({old_price} -> {price})")
                print(f"Eski: {old_price}")
                print(f"Yeni: {price}")
                print("----------")

    print("\nTarama tamamlandı.")
    print(f"Toplam ürün: {len(books)}")
    print(f"Yeni ürün: {new_products}")
    print(f"Güncellenen ürün: {updated_products}")

    if new_products == 0 and updated_products == 0:
        print("✓ Yeni ürün veya fiyat değişikliği bulunamadı.")

    logger.info("Scan completed.")