from datetime import datetime

import matplotlib.pyplot as plt


def plot_price_history(
    history: list[tuple[int, str, str]],
    product_name: str,
) -> None:
    if not history:
        print(
            "Bu ürün için fiyat geçmişi bulunamadı."
        )
        return

    currencies = {
        currency
        for _, currency, _ in history
    }

    if len(currencies) != 1:
        print(
            "Farklı para birimleri aynı grafikte "
            "gösterilemez."
        )
        return

    prices = [
        price_minor / 100
        for price_minor, _, _ in history
    ]
    dates = [
        datetime.fromisoformat(checked_at)
        for _, _, checked_at in history
    ]
    currency = currencies.pop()

    plt.figure(figsize=(10, 5))
    plt.plot(
        dates,
        prices,
        marker="o",
    )
    plt.title(
        f"Price History - {product_name}"
    )
    plt.xlabel("Date")
    plt.ylabel(f"Price ({currency})")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    plt.close()
