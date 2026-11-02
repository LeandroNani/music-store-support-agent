"""Catalogue lookups.

Every test maps to a line of docs/BUSINESS_RULES.md. The B numbers in the
docstrings are the conflicts between the store manual and the dataset.
"""

from decimal import Decimal

import pytest

from emporio.catalog import get_product_details, list_categories, search_products
from emporio.db import build_database

GIANNINI_GF3D = 96  # R$ 799.90, active, zero stock
GIANNINI_GNF3 = 101  # R$ 1049.00, only fits a R$ 1000 budget via PIX
SHELBY_7C = 113  # discontinued, zero stock
IBANEZ_BASS_2X = 136  # discontinued with 13 units in stock
TAKAMINE_GD20 = 95


@pytest.fixture
def db():
    connection = build_database()
    yield connection
    connection.close()


def test_categories_report_how_many_products_they_have(db):
    """B-05: three categories exist in the catalogue with nothing to sell.

    The agent needs the count to answer "do you have saxophones?" with "we work
    with them, none in stock right now" instead of "we don't sell those".
    """
    categories = {c.name: c.product_count for c in list_categories(db)}

    assert categories["Instrumentos de Sopro (Madeiras)"] == 0
    assert categories["Instrumentos de Sopro (Metais)"] == 0
    assert categories["Cordas Orquestrais"] == 0
    assert categories["Violões"] == 35


def test_search_leaves_out_discontinued_products(db):
    """B-01: a discontinued product is no longer part of the catalogue on offer."""
    result = search_products(db, category="Violões", max_price=Decimal("1000"))

    assert SHELBY_7C not in [item.product_id for item in result.items]


def test_search_keeps_out_of_stock_products_and_marks_them(db):
    """B-03: the product is still in the catalogue, it just has no units today."""
    result = search_products(db, category="Violões", max_price=Decimal("1000"), limit=20)

    out_of_stock = [i for i in result.items if i.product_id == GIANNINI_GF3D]
    assert out_of_stock, "a product with zero stock must still be listed"
    assert out_of_stock[0].in_stock is False


def test_search_price_filter_uses_the_price_the_customer_can_pay(db):
    """B-09: a product that only fits the budget via PIX is listed, and flagged.

    The Giannini GNF-3 lists at R$ 1049.00 and costs R$ 996.55 on PIX, so it
    belongs in a R$ 1000 search, with the condition made explicit.
    """
    result = search_products(db, category="Violões", max_price=Decimal("1000"), limit=20)

    match = [i for i in result.items if i.product_id == GIANNINI_GNF3]
    assert match, "a product that fits the budget on PIX must be listed"
    assert match[0].fits_budget_only_with_pix is True


def test_search_caps_the_page_and_reports_the_total(db):
    """Ten results per page, so the agent can offer to show more or to filter."""
    result = search_products(db, category="Violões", max_price=Decimal("1000"))

    assert len(result.items) == 10
    assert result.total == 14  # 15 fit the budget, minus the discontinued one
    assert result.has_more is True


def test_product_details_found_by_part_of_the_name(db):
    """A customer types "Takamine GD20", never the full catalogue name."""
    matches = get_product_details(db, name="takamine gd20")

    assert len(matches) == 1
    assert matches[0].product_id == TAKAMINE_GD20
    assert matches[0].price.final_price == Decimal("2199.00")


def test_discontinued_product_is_found_when_asked_for_by_name(db):
    """B-01: out of the search results, but offered if the customer asks for it.

    The Ibanez Bass 2X still has 13 units, and the store would rather sell them.
    """
    matches = get_product_details(db, name="Ibanez Bass 2X")

    assert len(matches) == 1
    assert matches[0].product_id == IBANEZ_BASS_2X
    assert matches[0].discontinued is True
    assert matches[0].in_stock is True


def test_accents_do_not_break_a_name_search(db):
    """Customers type "eletrico" as often as "elétrico"."""
    with_accent = search_products(db, query="Elétrico", limit=50)
    without_accent = search_products(db, query="eletrico", limit=50)

    assert with_accent.total == without_accent.total
    assert with_accent.total > 0
