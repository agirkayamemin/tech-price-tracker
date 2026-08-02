from unittest.mock import patch

import pytest

from src.database import LegacyDatabaseError
from src.main import (
    main,
    run_history,
    run_products,
    run_scan,
)


def test_scan_command_uses_one_page_by_default():
    with patch(
        "src.main.run_scan",
        return_value=0,
    ) as mock_scan:
        result = main(["scan"])

    assert result == 0
    mock_scan.assert_called_once_with(1)


@pytest.mark.parametrize(
    ("arguments", "expected_pages"),
    [
        (["scan", "--max-pages", "5"], 5),
        (["scan", "--all-pages"], 50),
    ],
)
def test_scan_page_options(
    arguments,
    expected_pages,
):
    with patch(
        "src.main.run_scan",
        return_value=0,
    ) as mock_scan:
        result = main(arguments)

    assert result == 0
    mock_scan.assert_called_once_with(
        expected_pages
    )


def test_no_command_shows_help(capsys):
    result = main([])
    output = capsys.readouterr().out

    assert result == 0
    assert "usage:" in output


def test_products_command_passes_limit():
    with patch(
        "src.main.run_products",
        return_value=[],
    ) as mock_products:
        result = main(
            ["products", "--limit", "3"]
        )

    assert result == 0
    mock_products.assert_called_once_with(3)


def test_history_command_passes_product_id():
    with patch(
        "src.main.run_history",
        return_value=0,
    ) as mock_history:
        result = main(
            ["history", "--product-id", "7"]
        )

    assert result == 0
    mock_history.assert_called_once_with(7)


@pytest.mark.parametrize(
    "arguments",
    [
        ["scan", "--max-pages", "0"],
        ["scan", "--max-pages", "51"],
        [
            "scan",
            "--max-pages",
            "2",
            "--all-pages",
        ],
        ["products", "--limit", "0"],
        ["history", "--product-id", "abc"],
    ],
)
def test_invalid_cli_usage_returns_exit_code_two(
    arguments,
):
    with pytest.raises(SystemExit) as error:
        main(arguments)

    assert error.value.code == 2


def test_run_scan_returns_failure_for_page_errors():
    summary = {
        "pages_scanned": 1,
        "products_found": 20,
        "created": 0,
        "updated": 0,
        "unchanged": 20,
        "failed_pages": 1,
    }

    with (
        patch("src.main.connect_db"),
        patch(
            "src.main.scrape",
            return_value=summary,
        ) as mock_scrape,
    ):
        result = run_scan(max_pages=3)

    assert result == 1
    mock_scrape.assert_called_once_with(
        max_pages=3
    )


def test_run_products_displays_v2_records(capsys):
    products = [
        (
            7,
            "books.toscrape.com",
            "https://example.com/book",
            "Test Product",
            1050,
            "GBP",
        )
    ]

    with (
        patch("src.main.connect_db"),
        patch(
            "src.main.list_products",
            return_value=products,
        ),
    ):
        result = run_products(limit=1)

    output = capsys.readouterr().out

    assert result == products
    assert (
        "7. Test Product - £10.50 "
        "[books.toscrape.com]"
    ) in output


def test_history_selection_uses_product_id():
    products = [
        (
            7,
            "books.toscrape.com",
            "https://example.com/book",
            "Test Product",
            1000,
            "GBP",
        )
    ]
    history = [
        (
            1000,
            "GBP",
            "2026-08-02T10:00:00+00:00",
        )
    ]

    with (
        patch(
            "src.main.run_products",
            return_value=products,
        ),
        patch(
            "src.main.list_price_history",
            return_value=history,
        ) as mock_history,
        patch(
            "src.main.plot_price_history"
        ) as mock_plot,
    ):
        result = run_history(product_id=7)

    assert result == 0
    mock_history.assert_called_once_with(7)
    mock_plot.assert_called_once_with(
        history,
        "Test Product",
    )


def test_main_reports_legacy_database(capsys):
    with patch(
        "src.main.run_products",
        side_effect=LegacyDatabaseError(
            "Legacy database schema detected."
        ),
    ):
        result = main(["products"])

    output = capsys.readouterr().out

    assert result == 1
    assert "Veritabanı güncellenmeli" in output
