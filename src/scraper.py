from database import get_product, save_product, update_price
import requests
from bs4 import BeautifulSoup

def scrape():
    response = requests.get("https://books.toscrape.com/")
    response.encoding = "utf-8"
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    books = soup.find_all("article", class_="product_pod")

    for book in books:
        name = book.find("h3").find("a")["title"]
        price = book.find("p", class_="price_color").text
        product = get_product(name)

        if product is None:
            save_product(name, price)
            print("Yeni ürün eklendi.")
        else:
            old_price = product[2]

            if old_price != price:
                update_price(name, price)
                print(f"Fiyat değişti: {old_price} -> {price}")
            else:
                print("Fiyat değişmedi.")   

        print(name)
        print(price)
        print("----------")