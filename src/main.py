from src.scraper import scrape
from src.database import connect_db

def main():
    print("Tech Price Tracker")
    connect_db()
    scrape()

if __name__ == "__main__": 
    main()
