from scraper import scrape
from database import connect_db

def main():
    print("Tech Price Tracker")
    connect_db()
    scrape()

if __name__ == "__main__": 
    main()
