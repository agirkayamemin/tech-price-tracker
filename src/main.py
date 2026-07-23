from src.scraper import scrape
from src.database import (
    connect_db,
    get_all_products,
    get_price_history
)
from src.visualization import plot_price_history


def main():
    print("Tech Price Tracker")

    connect_db()

    scrape()

    products = get_all_products()

    if not products:
        print("\nVeritabanında ürün bulunamadı.")
        return

    print("\n--------------------------------")
    print("FİYAT GEÇMİŞİ")
    print("--------------------------------")

    for index, product in enumerate(products, start=1):
        print(
            f"{index}. {product[1]} - {product[2]}"
        )

    print("\nGrafiğini görmek istediğiniz ürün numarasını girin.")
    print("Çıkmak için Enter'a basın.")

    choice = input("\nSeçiminiz: ")

    if choice == "":
        print("Program sonlandırıldı.")
        return

    try:
        choice = int(choice)

        if choice < 1 or choice > len(products):
            print("Geçersiz ürün numarası.")
            return

    except ValueError:
        print("Lütfen geçerli bir sayı girin.")
        return

    selected_product = products[choice - 1]

    product_id = selected_product[0]
    product_name = selected_product[1]

    history = get_price_history(product_id)

    plot_price_history(
        history,
        product_name
    )


if __name__ == "__main__":
    main()