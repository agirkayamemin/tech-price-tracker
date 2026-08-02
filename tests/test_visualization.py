from datetime import timedelta
from unittest.mock import patch

from src.visualization import plot_price_history


def test_plot_price_history_uses_minor_units_and_utc():
    history = [
        (
            1000,
            "GBP",
            "2026-08-02T10:00:00+00:00",
        ),
        (
            1550,
            "GBP",
            "2026-08-02T11:00:00+00:00",
        ),
    ]

    with (
        patch(
            "src.visualization.plt.plot"
        ) as mock_plot,
        patch("src.visualization.plt.show"),
    ):
        plot_price_history(
            history,
            "Test Product",
        )

    dates, prices = mock_plot.call_args.args

    assert prices == [10.0, 15.5]
    assert dates[0].utcoffset() == timedelta(0)


def test_plot_price_history_empty(capsys):
    plot_price_history(
        [],
        "Test Product",
    )

    output = capsys.readouterr().out

    assert (
        "Bu ürün için fiyat geçmişi bulunamadı."
        in output
    )


def test_plot_price_history_rejects_mixed_currencies(
    capsys,
):
    history = [
        (
            1000,
            "GBP",
            "2026-08-02T10:00:00+00:00",
        ),
        (
            1500,
            "USD",
            "2026-08-02T11:00:00+00:00",
        ),
    ]

    with patch(
        "src.visualization.plt.show"
    ) as mock_show:
        plot_price_history(
            history,
            "Test Product",
        )

    output = capsys.readouterr().out

    assert "Farklı para birimleri" in output
    mock_show.assert_not_called()
