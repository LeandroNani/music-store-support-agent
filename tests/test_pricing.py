"""Pricing rules.

Every test here maps to one line of docs/BUSINESS_RULES.md. The section marked
in each docstring is the section of the store's policy manual the rule comes from.
"""

from decimal import Decimal

import pytest

from emporio.db import build_database
from emporio.pricing import max_installments, price_for_product

# Products used below, straight from the dataset.
YAMAHA_C40 = 81  # R$ 599.90, no promotion
KALANI_TENOR = 127  # R$ 359.00, 10% promotion, active
GIANNINI_GF3D = 96  # R$ 799.90, two promotions, both expired
CRAFTER_HT100 = 90  # R$ 2399.00, 18% promotion, active


@pytest.fixture
def db():
    connection = build_database()
    yield connection
    connection.close()


def test_pix_discount_applies_to_list_price(db):
    """Manual 3: PIX gives 5% off the list price."""
    price = price_for_product(db, YAMAHA_C40)

    assert price.list_price == Decimal("599.90")
    assert price.final_price == Decimal("599.90")
    assert price.pix_price == Decimal("569.91")
    assert price.pix_discount_applies is True


def test_pix_discount_does_not_stack_on_promotional_price(db):
    """Manual 6.2: the PIX discount does not apply on an already discounted price.

    This is the rule most likely to break unnoticed, because 10% plus 5% produces
    a number that looks plausible.
    """
    price = price_for_product(db, KALANI_TENOR)

    assert price.list_price == Decimal("359.00")
    assert price.discount_percent == Decimal("10")
    assert price.final_price == Decimal("323.10")

    assert price.pix_price == Decimal("323.10")
    assert price.pix_discount_applies is False
    # 359.00 * 0.90 * 0.95 would be 306.95. Stacking is what we are ruling out.
    assert price.pix_price != Decimal("306.95")


def test_expired_promotions_are_ignored(db):
    """Manual 7.3: never promise a discount that is no longer running.

    Product 96 carries an 18% and a 40% promotion in the dataset. Both are expired.
    """
    price = price_for_product(db, GIANNINI_GF3D)

    assert price.discount_percent is None
    assert price.final_price == Decimal("799.90")
    assert price.pix_discount_applies is True
    assert price.pix_price == Decimal("759.91")


def test_promotions_never_stack_with_each_other(db):
    """Manual 6.2: promotions are not cumulative.

    No product in the dataset has two active promotions at the same time, so the
    second one is inserted here to exercise the rule.
    """
    db.execute(
        "INSERT INTO promotions VALUES (999, ?, 20, 'Segunda promocao', 1)",
        (KALANI_TENOR,),
    )

    price = price_for_product(db, KALANI_TENOR)

    # The larger discount wins; 10% and 20% are never added into 30%.
    assert price.discount_percent == Decimal("20")
    assert price.final_price == Decimal("287.20")


def test_max_installments_respects_the_minimum_for_the_band(db):
    """Manual 3.1: 4x to 6x require a R$ 80.00 minimum, 7x to 12x require R$ 100.00.

    R$ 599.90 in 6x is R$ 99.98, which clears the R$ 80.00 minimum. In 7x it would
    be R$ 85.70, below the R$ 100.00 minimum of that band, so 6x is the ceiling.
    """
    price = price_for_product(db, YAMAHA_C40)

    assert price.max_installments == 6
    assert price.installment_value == Decimal("99.98")


def test_installments_are_calculated_on_the_discounted_price(db):
    """Manual 3.1 combined with 6.2: the customer pays the promotional price.

    R$ 359.00 less 10% is R$ 323.10. In 4x that is R$ 80.78, which clears the
    R$ 80.00 minimum. In 5x it would be R$ 64.62, below it.
    """
    price = price_for_product(db, KALANI_TENOR)

    assert price.max_installments == 4
    assert price.installment_value == Decimal("80.78")


def test_combined_payment_uses_the_price_actually_charged(db):
    """Manual 3.1: combining payment methods is allowed above R$ 2000.00.

    The Crafter HT-100 lists at R$ 2399.00, but its active 18% promotion brings it
    to R$ 1967.18. The customer pays under R$ 2000.00, so combining is not allowed.
    """
    price = price_for_product(db, CRAFTER_HT100)

    assert price.final_price == Decimal("1967.18")
    assert price.allows_combined_payment is False


def test_combined_payment_allowed_above_the_threshold(db):
    """Manual 3.1: above R$ 2000.00 the customer may combine payment methods."""
    price = price_for_product(db, 93)  # Martin D-28, R$ 11499.00, no active promotion

    assert price.final_price == Decimal("11499.00")
    assert price.allows_combined_payment is True


def test_installment_floor_up_to_three_times():
    """Manual 3.1: up to 3x, the installment itself may not fall below R$ 50.00.

    No product in the catalogue reaches this floor, since the cheapest is
    R$ 159.90, which is R$ 53.30 in 3x. The rule is exercised on the amount
    directly so it is still covered when the catalogue changes.
    """
    count, value = max_installments(Decimal("120.00"))

    # 3x would be R$ 40.00, under the floor, so 2x is the ceiling.
    assert count == 2
    assert value == Decimal("60.00")
