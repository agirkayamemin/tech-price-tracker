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

        print(name)
        print(price)
        print("----------")