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
- Unit tests for database, CLI, scraper, and visualization
- Command-line interface for scanning, listing products, and viewing price history

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
│   ├── test_database.py
│   ├── test_main.py
│   ├── test_scraper.py
│   └── test_visualization.py
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

Scan the source website and update the local database:

```bash
python -m src.main scan
```

List products stored in the database:

```bash
python -m src.main products
```

Select a product and display its price-history chart:

```bash
python -m src.main history
```

Display the command help:

```bash
python -m src.main
```

## Tests

```bash
pytest
```

Current test suite:

```text
16 passed
```

## Future Improvements

- Support multiple websites
- Email notifications
- Scheduled automatic scans
- Deployment to a continuously running server
