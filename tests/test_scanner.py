from pathlib import Path
from unittest.mock import Mock, call, patch

import pytest
import requests

from src.models import ProductData
from src.scraper import (
    PageFetchError,
    fetch_page,
    save_scan_results,
    scan_catalog,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_fetch_page_returns_html():
    url = "https://books.toscrape.com/"

    mock_response = Mock()
    mock_response.text = "<html>catalog</html>"

    with patch(
        "src.scraper.requests.get",
        return_value=mock_response,
    ) as mock_get:
        html = fetch_page(
            url,
            timeout=5,
        )

    assert html == "<html>catalog</html>"
    mock_get.assert_called_once_with(
        url,
        timeout=5,
    )
    mock_response.raise_for_status.assert_called_once_with()
    assert mock_response.encoding == "utf-8"


def test_fetch_page_wraps_timeout():
    url = "https://books.toscrape.com/"

    with (
        patch(
            "src.scraper.requests.get",
            side_effect=requests.Timeout(
                "request timed out"
            ),
        ),
        pytest.raises(
            PageFetchError,
            match="books.toscrape.com",
        ),
    ):
        fetch_page(url)


def test_fetch_page_wraps_http_error():
    url = "https://books.toscrape.com/"

    mock_response = Mock()
    mock_response.raise_for_status.side_effect = (
        requests.HTTPError("500 Server Error")
    )

    with (
        patch(
            "src.scraper.requests.get",
            return_value=mock_response,
        ),
        pytest.raises(
            PageFetchError,
            match="books.toscrape.com",
        ),
    ):
        fetch_page(url)


def test_save_scan_results_counts_statuses():
    products = [
        ProductData(
            source="books.toscrape.com",
            product_url="https://example.com/book-1",
            name="Book 1",
            price_minor=1000,
            currency="GBP",
        ),
        ProductData(
            source="books.toscrape.com",
            product_url="https://example.com/book-2",
            name="Book 2",
            price_minor=2000,
            currency="GBP",
        ),
        ProductData(
            source="books.toscrape.com",
            product_url="https://example.com/book-3",
            name="Book 3",
            price_minor=3000,
            currency="GBP",
        ),
    ]

    with patch(
        "src.scraper.upsert_product",
        side_effect=[
            "created",
            "updated",
            "unchanged",
        ],
    ) as mock_upsert:
        summary = save_scan_results(
            products,
            "test.db",
            checked_at=(
                "2026-08-02T10:00:00+00:00"
            ),
        )

    assert summary == {
        "created": 1,
        "updated": 1,
        "unchanged": 1,
    }
    assert mock_upsert.call_count == 3


def test_scan_catalog_scans_one_page_by_default():
    html = (
        FIXTURES_DIR / "catalog_page_1.html"
    ).read_text(encoding="utf-8")

    with (
        patch(
            "src.scraper.fetch_page",
            return_value=html,
        ) as mock_fetch,
        patch(
            "src.scraper.save_scan_results",
            return_value={
                "created": 1,
                "updated": 0,
                "unchanged": 0,
            },
        ) as mock_save,
    ):
        summary = scan_catalog(
            db_path="test.db",
        )

    assert summary == {
        "pages_scanned": 1,
        "products_found": 1,
        "created": 1,
        "updated": 0,
        "unchanged": 0,
        "failed_pages": 0,
    }
    mock_fetch.assert_called_once_with(
        "https://books.toscrape.com/",
        timeout=10,
    )
    assert mock_save.call_count == 1


def test_scan_catalog_follows_pagination():
    first_page_html = (
        FIXTURES_DIR / "catalog_page_1.html"
    ).read_text(encoding="utf-8")
    second_page_html = (
        FIXTURES_DIR / "catalog_page_2.html"
    ).read_text(encoding="utf-8")

    with (
        patch(
            "src.scraper.fetch_page",
            side_effect=[
                first_page_html,
                second_page_html,
            ],
        ) as mock_fetch,
        patch(
            "src.scraper.save_scan_results",
            side_effect=[
                {
                    "created": 1,
                    "updated": 0,
                    "unchanged": 0,
                },
                {
                    "created": 1,
                    "updated": 0,
                    "unchanged": 0,
                },
            ],
        ),
    ):
        summary = scan_catalog(
            db_path="test.db",
            max_pages=5,
            request_delay=0,
        )

    assert summary == {
        "pages_scanned": 2,
        "products_found": 2,
        "created": 2,
        "updated": 0,
        "unchanged": 0,
        "failed_pages": 0,
    }
    assert mock_fetch.call_args_list == [
        call(
            "https://books.toscrape.com/",
            timeout=10,
        ),
        call(
            (
                "https://books.toscrape.com/"
                "catalogue/page-2.html"
            ),
            timeout=10,
        ),
    ]


def test_scan_catalog_rejects_unsafe_page_limit():
    with (
        patch(
            "src.scraper.fetch_page",
            side_effect=AssertionError(
                "Network request should not happen."
            ),
        ),
        pytest.raises(
            ValueError,
            match="cannot exceed",
        ),
    ):
        scan_catalog(
            db_path="test.db",
            max_pages=51,
        )


def test_scan_catalog_rejects_zero_page_limit():
    with (
        patch(
            "src.scraper.fetch_page",
            side_effect=AssertionError(
                "Network request should not happen."
            ),
        ),
        pytest.raises(
            ValueError,
            match="at least 1",
        ),
    ):
        scan_catalog(
            db_path="test.db",
            max_pages=0,
        )


def test_scan_catalog_rejects_negative_delay():
    with (
        patch(
            "src.scraper.fetch_page",
            side_effect=AssertionError(
                "Network request should not happen."
            ),
        ),
        pytest.raises(
            ValueError,
            match="cannot be negative",
        ),
    ):
        scan_catalog(
            db_path="test.db",
            request_delay=-0.1,
        )


def test_scan_catalog_waits_between_pages():
    first_page_html = (
        FIXTURES_DIR / "catalog_page_1.html"
    ).read_text(encoding="utf-8")
    second_page_html = (
        FIXTURES_DIR / "catalog_page_2.html"
    ).read_text(encoding="utf-8")

    with (
        patch(
            "src.scraper.fetch_page",
            side_effect=[
                first_page_html,
                second_page_html,
            ],
        ),
        patch(
            "src.scraper.save_scan_results",
            return_value={
                "created": 1,
                "updated": 0,
                "unchanged": 0,
            },
        ),
        patch(
            "src.scraper.time.sleep"
        ) as mock_sleep,
    ):
        scan_catalog(
            db_path="test.db",
            max_pages=5,
            request_delay=0.25,
        )

    mock_sleep.assert_called_once_with(0.25)


def test_scan_catalog_preserves_results_on_page_error(
    caplog,
):
    first_page_html = (
        FIXTURES_DIR / "catalog_page_1.html"
    ).read_text(encoding="utf-8")

    with (
        patch(
            "src.scraper.fetch_page",
            side_effect=[
                first_page_html,
                PageFetchError(
                    "second page failed"
                ),
            ],
        ),
        patch(
            "src.scraper.save_scan_results",
            return_value={
                "created": 1,
                "updated": 0,
                "unchanged": 0,
            },
        ),
    ):
        summary = scan_catalog(
            db_path="test.db",
            max_pages=5,
            request_delay=0,
        )

    assert summary == {
        "pages_scanned": 1,
        "products_found": 1,
        "created": 1,
        "updated": 0,
        "unchanged": 0,
        "failed_pages": 1,
    }
    assert "Failed to scan page" in caplog.text
