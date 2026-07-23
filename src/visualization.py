import matplotlib.pyplot as plt
from datetime import datetime


def plot_price_history(history, product_name):
    if not history:
        print("Bu ürün için fiyat geçmişi bulunamadı.")
        return

    prices = []
    dates = []

    for price, checked_at in history:
        price_value = float(
            price.replace("£", "").strip()
        )

        date_value = datetime.strptime(
            checked_at,
            "%Y-%m-%d %H:%M:%S"
        )

        prices.append(price_value)
        dates.append(date_value)

    plt.figure(figsize=(10, 5))

    plt.plot(
        dates,
        prices,
        marker="o"
    )

    plt.title(
        f"Price History - {product_name}"
    )

    plt.xlabel("Date")
    plt.ylabel("Price (£)")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.show()