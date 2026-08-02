import time

import requests

from src.catalog_parser import (
    find_next_page,
    parse_products,
)
from src.config import DATABASE_PATH, URL
from src.database import upsert_product
from src.logger import logger
from src.models import ProductData


MAX_PAGE_LIMIT = 50


class PageFetchError(RuntimeError):
    pass


def fetch_page(
    url: str,
    timeout: int = 10,
) -> str:
    try:
        response = requests.get(
            url,
            timeout=timeout,
        )
        response.raise_for_status()
        response.encoding = "utf-8"
    except requests.RequestException as error:
        raise PageFetchError(
            f"Failed to fetch page: {url}"
        ) from error

    return response.text


def save_scan_results(
    products: list[ProductData],
    db_path,
    *,
    checked_at: str | None = None,
) -> dict[str, int]:
    summary = {
        "created": 0,
        "updated": 0,
        "unchanged": 0,
    }

    for product in products:
        status = upsert_product(
            product,
            db_path,
            checked_at=checked_at,
        )
        summary[status] += 1

    return summary


def scan_catalog(
    start_url: str = URL,
    db_path=DATABASE_PATH,
    *,
    max_pages: int = 1,
    timeout: int = 10,
    request_delay: float = 0.5,
) -> dict[str, int]:
    if max_pages < 1:
        raise ValueError(
            "max_pages must be at least 1."
        )

    if max_pages > MAX_PAGE_LIMIT:
        raise ValueError(
            f"max_pages cannot exceed "
            f"{MAX_PAGE_LIMIT}."
        )

    if request_delay < 0:
        raise ValueError(
            "request_delay cannot be negative."
        )

    summary = {
        "pages_scanned": 0,
        "products_found": 0,
        "created": 0,
        "updated": 0,
        "unchanged": 0,
        "failed_pages": 0,
    }
    current_url = start_url

    while (
        current_url is not None
        and summary["pages_scanned"] < max_pages
    ):
        try:
            html = fetch_page(
                current_url,
                timeout=timeout,
            )
        except PageFetchError as error:
            summary["failed_pages"] += 1
            logger.error(
                "Failed to scan page %s: %s",
                current_url,
                error,
            )
            break

        products = parse_products(
            html,
            page_url=current_url,
        )
        save_summary = save_scan_results(
            products,
            db_path,
        )

        summary["pages_scanned"] += 1
        summary["products_found"] += len(products)
        summary["created"] += save_summary["created"]
        summary["updated"] += save_summary["updated"]
        summary["unchanged"] += (
            save_summary["unchanged"]
        )

        if summary["pages_scanned"] >= max_pages:
            break

        next_url = find_next_page(
            html,
            page_url=current_url,
        )

        if next_url is None:
            break

        if request_delay > 0:
            time.sleep(request_delay)

        current_url = next_url

    return summary


def scrape(
    database_path=None,
    *,
    max_pages: int = 1,
    request_delay: float = 0.5,
) -> dict[str, int]:
    db_path = (
        DATABASE_PATH
        if database_path is None
        else database_path
    )

    logger.info("Scan started.")

    summary = scan_catalog(
        db_path=db_path,
        max_pages=max_pages,
        request_delay=request_delay,
    )

    print("\nTarama tamamlandı.")
    print(
        f"Taranan sayfa: "
        f"{summary['pages_scanned']}"
    )
    print(
        f"Toplam ürün: "
        f"{summary['products_found']}"
    )
    print(f"Yeni ürün: {summary['created']}")
    print(
        f"Güncellenen ürün: "
        f"{summary['updated']}"
    )
    print(
        f"Değişmeyen ürün: "
        f"{summary['unchanged']}"
    )
    print(
        f"Başarısız sayfa: "
        f"{summary['failed_pages']}"
    )

    if (
        summary["created"] == 0
        and summary["updated"] == 0
        and summary["failed_pages"] == 0
    ):
        print(
            "✓ Yeni ürün veya fiyat değişikliği "
            "bulunamadı."
        )

    logger.info("Scan completed.")

    return summary
