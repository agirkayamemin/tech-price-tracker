# Tech Price Tracker

A Python project that tracks product prices using web scraping and SQLite.

## Technologies

- Python
- Requests
- BeautifulSoup4
- SQLite3

## Project Structure

```text
tech_price_tracker/
│
├── data/
├── src/
├── tests/
├── README.md
└── .gitignore
```

## Current Features

- Scrape real websites
- Parse HTML with BeautifulSoup
- Extract product names and prices
- Store products in SQLite
- Prevent duplicate products
- Detect price changes
- Update product prices automatically
- Store configuration in a dedicated `config.py` file
- Display a clean scan summary after each run
- Handle network and HTTP errors gracefully
- Store complete price history

## Upcoming Features

- Track price history
- Email notifications
- Scheduled automatic checks
- Support multiple websites
- Error handling and logging
- Track price history