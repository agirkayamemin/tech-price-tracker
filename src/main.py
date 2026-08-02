import argparse
import sqlite3

from src.database import (
    LegacyDatabaseError,
    connect_db,
    list_price_history,
    list_products,
)
from src.pricing import format_price
from src.scraper import MAX_PAGE_LIMIT, scrape
from src.visualization import plot_price_history


def positive_int(value: str) -> int:
    try:
        parsed_value = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "value must be an integer"
        ) from error

    if parsed_value < 1:
        raise argparse.ArgumentTypeError(
            "value must be at least 1"
        )

    return parsed_value


def page_count(value: str) -> int:
    parsed_value = positive_int(value)

    if parsed_value > MAX_PAGE_LIMIT:
        raise argparse.ArgumentTypeError(
            f"value cannot exceed {MAX_PAGE_LIMIT}"
        )

    return parsed_value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ürün fiyatlarını takip eder."
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="komutlar",
    )

    scan_parser = subparsers.add_parser(
        "scan",
        help="Siteyi tarar ve fiyatları günceller.",
    )
    scan_options = (
        scan_parser.add_mutually_exclusive_group()
    )
    scan_options.add_argument(
        "--max-pages",
        type=page_count,
        default=1,
        metavar="N",
        help=(
            "En fazla N katalog sayfası tarar "
            f"(üst sınır: {MAX_PAGE_LIMIT})."
        ),
    )
    scan_options.add_argument(
        "--all-pages",
        action="store_true",
        help=(
            "Kataloğu güvenli üst sınıra kadar "
            "tarar."
        ),
    )

    products_parser = subparsers.add_parser(
        "products",
        help="Kayıtlı ürünleri listeler.",
    )
    products_parser.add_argument(
        "--limit",
        type=positive_int,
        metavar="N",
        help="İlk N ürünü listeler.",
    )

    history_parser = subparsers.add_parser(
        "history",
        help="Bir ürünün fiyat geçmişini gösterir.",
    )
    history_parser.add_argument(
        "--product-id",
        type=positive_int,
        metavar="ID",
        help=(
            "Etkileşimli seçim yerine ürün "
            "kimliğini kullanır."
        ),
    )

    return parser


def run_scan(max_pages: int = 1) -> int:
    connect_db()
    summary = scrape(max_pages=max_pages)

    if summary["failed_pages"] > 0:
        return 1

    return 0


def run_products(
    limit: int | None = None,
):
    connect_db()
    products = list_products()

    if limit is not None:
        products = products[:limit]

    if not products:
        print("\nVeritabanında ürün bulunamadı.")
        return []

    print("\n--------------------------------")
    print("ÜRÜNLER")
    print("--------------------------------")

    for product in products:
        product_id = product[0]
        source = product[1]
        name = product[3]
        price_minor = product[4]
        currency = product[5]
        price = format_price(
            price_minor,
            currency,
        )

        print(
            f"{product_id}. {name} - "
            f"{price} [{source}]"
        )

    return products


def run_history(
    product_id: int | None = None,
) -> int:
    products = run_products()

    if not products:
        return 0

    if product_id is None:
        print(
            "\nGrafiğini görmek istediğiniz "
            "ürünün ID değerini girin."
        )
        print("Çıkmak için Enter'a basın.")

        choice = input("\nSeçiminiz: ")

        if choice == "":
            print("Program sonlandırıldı.")
            return 0

        try:
            product_id = int(choice)
        except ValueError:
            print("Lütfen geçerli bir sayı girin.")
            return 2

    selected_product = next(
        (
            product
            for product in products
            if product[0] == product_id
        ),
        None,
    )

    if selected_product is None:
        print("Geçersiz ürün ID değeri.")
        return 1

    product_name = selected_product[3]
    history = list_price_history(product_id)

    plot_price_history(
        history,
        product_name,
    )

    return 0


def main(argv=None) -> int:
    print("Tech Price Tracker")

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "scan":
            max_pages = (
                MAX_PAGE_LIMIT
                if args.all_pages
                else args.max_pages
            )
            return run_scan(max_pages)

        if args.command == "products":
            run_products(args.limit)
            return 0

        if args.command == "history":
            return run_history(args.product_id)
    except LegacyDatabaseError as error:
        print(f"\nVeritabanı güncellenmeli: {error}")
        return 1
    except sqlite3.Error as error:
        print(f"\nVeritabanı hatası: {error}")
        return 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
