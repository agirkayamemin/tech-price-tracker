import pytest

from src.pricing import parse_price


@pytest.mark.parametrize(
    ("price_text", "expected"),
    [
        ("£51.77", (5177, "GBP")),
        ("  £10.50  ", (1050, "GBP")),
        ("£0.00", (0, "GBP")),
        ("£12.3", (1230, "GBP")),
    ],
)
def test_parse_gbp_price(price_text, expected):
    assert parse_price(price_text) == expected


@pytest.mark.parametrize(
    "price_text",
    [
        "",
        None,
        "51.77",
        "$51.77",
        "£invalid",
        "£-1.00",
        "£1.999",
    ],
)
def test_parse_price_rejects_invalid_values(price_text):
    with pytest.raises(ValueError):
        parse_price(price_text)