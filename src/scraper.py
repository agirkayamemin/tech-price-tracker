import requests
from bs4 import BeautifulSoup


def scrape():
    print("Scraper çalıştı.")

    with open("data/sample_page.html", "r", encoding="utf-8") as file:
        html = file.read()

    soup = BeautifulSoup(html, "html.parser")

    product = soup.find("h2")
    price = soup.find("span", class_="price")

    print("Ürün:", product.text.strip())
    print("Fiyat:", price.text.strip())