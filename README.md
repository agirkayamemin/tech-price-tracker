# Tech Price Tracker

A Python application that scrapes product prices, stores price history, detects changes, and visualizes historical price data.

## Technologies

- Python
- Requests
- BeautifulSoup4
- SQLite3
- Matplotlib
- Pytest

## Features

- Scrape product names and prices from a website
- Store products in SQLite
- Prevent duplicate products
- Detect and update price changes
- Store complete price history
- Display price history charts
- Handle HTTP and network errors
- Log application events
- Unit tests for database, scraper, and visualization

## Project Structure

```text
tech_price_tracker/
├── data/
├── src/
│   ├── config.py
│   ├── database.py
│   ├── logger.py
│   ├── main.py
│   ├── scraper.py
│   └── visualization.py
├── tests/
├── pytest.ini
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

```bash
git clone https://github.com/agirkayamemin/tech-price-tracker.git
cd tech-price-tracker

python -m venv venv
source venv/Scripts/activate

pip install -r requirements.txt
```

## Usage

```bash
python -m src.main
```

The application scans products, updates changed prices, and lets the user select a product to display its price-history chart.

## Tests

```bash
pytest
```

Current test suite:

```text
11 passed
```

## Future Improvements

- Support multiple websites
- Command-line interface
- Email notifications
- Scheduled automatic scans
- Deployment to a continuously running server