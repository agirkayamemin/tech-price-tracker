from unittest.mock import patch

from src.main import main, run_history


def test_scan_command():
    with (
        patch("src.main.run_scan") as mock_scan,
        patch("src.main.run_products") as mock_products,
        patch("src.main.run_history") as mock_history,
    ):
        main(["scan"])

    mock_scan.assert_called_once_with()
    mock_products.assert_not_called()
    mock_history.assert_not_called()


def test_no_command_shows_help(capsys):
    with (
        patch("src.main.run_scan") as mock_scan,
        patch("src.main.run_products") as mock_products,
        patch("src.main.run_history") as mock_history,
    ):
        main([])

    captured = capsys.readouterr()

    assert "usage:" in captured.out
    mock_scan.assert_not_called()
    mock_products.assert_not_called()
    mock_history.assert_not_called()


def test_products_command():
    with (
        patch("src.main.run_scan") as mock_scan,
        patch("src.main.run_products") as mock_products,
        patch("src.main.run_history") as mock_history,
    ):
        main(["products"])

    mock_scan.assert_not_called()
    mock_products.assert_called_once_with()
    mock_history.assert_not_called()


def test_history_command():
    with (
        patch("src.main.run_scan") as mock_scan,
        patch("src.main.run_products") as mock_products,
        patch("src.main.run_history") as mock_history,
    ):
        main(["history"])

    mock_scan.assert_not_called()
    mock_products.assert_not_called()
    mock_history.assert_called_once_with()


def test_history_selection():
    products = [
        (1, "Test Product", "£10.00")
    ]
    history = [
        ("£10.00", "2026-07-24 10:00:00")
    ]

    with (
        patch("src.main.run_products", return_value=products),
        patch("builtins.input", return_value="1"),
        patch(
            "src.main.get_price_history",
            return_value=history
        ) as mock_get_history,
        patch("src.main.plot_price_history") as mock_plot,
    ):
        run_history()

    mock_get_history.assert_called_once_with(1)
    mock_plot.assert_called_once_with(
        history,
        "Test Product"
    )