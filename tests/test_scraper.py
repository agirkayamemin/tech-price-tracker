from unittest.mock import patch

from src.scraper import scrape


def test_scrape_prints_catalog_summary(
    tmp_path,
    capsys,
):
    test_db = tmp_path / "test.db"
    summary = {
        "pages_scanned": 2,
        "products_found": 40,
        "created": 5,
        "updated": 2,
        "unchanged": 33,
        "failed_pages": 0,
    }

    with patch(
        "src.scraper.scan_catalog",
        return_value=summary,
    ) as mock_scan:
        result = scrape(
            test_db,
            max_pages=2,
            request_delay=0,
        )

    output = capsys.readouterr().out

    assert result == summary
    assert "Taranan sayfa: 2" in output
    assert "Toplam ürün: 40" in output
    assert "Yeni ürün: 5" in output
    assert "Güncellenen ürün: 2" in output
    mock_scan.assert_called_once_with(
        db_path=test_db,
        max_pages=2,
        request_delay=0,
    )


def test_scrape_reports_failed_pages(
    tmp_path,
    capsys,
):
    test_db = tmp_path / "test.db"
    summary = {
        "pages_scanned": 1,
        "products_found": 20,
        "created": 0,
        "updated": 0,
        "unchanged": 20,
        "failed_pages": 1,
    }

    with patch(
        "src.scraper.scan_catalog",
        return_value=summary,
    ):
        scrape(
            test_db,
            max_pages=2,
            request_delay=0,
        )

    output = capsys.readouterr().out

    assert "Başarısız sayfa: 1" in output