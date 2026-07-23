from src.visualization import plot_price_history


def test_plot_price_history(monkeypatch):
    history = [
        ("£10.00", "2026-07-17 10:00:00"),
        ("£15.00", "2026-07-18 10:00:00"),
        ("£20.00", "2026-07-19 10:00:00"),
    ]

    def mock_show():
        pass

    monkeypatch.setattr(
        "src.visualization.plt.show",
        mock_show
    )

    plot_price_history(
        history,
        "Test Product"
    )

def test_plot_price_history_empty(monkeypatch, capsys):
    def mock_show():
        pass

    monkeypatch.setattr(
        "src.visualization.plt.show",
        mock_show
    )

    plot_price_history(
        [],
        "Test Product"
    )

    captured = capsys.readouterr()

    assert "Bu ürün için fiyat geçmişi bulunamadı." in captured.out