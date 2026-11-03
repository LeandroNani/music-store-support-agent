"""Pricing rules from the store's policy manual.

Every rule here is enforced in code rather than described in the prompt, so the
model never sees a raw price: it receives the figure the customer actually pays
and only has to communicate it. See docs/BUSINESS_RULES.md for the rule sources.

Money is converted to Decimal on the way out. The CSV columns load as REAL,
which holds these magnitudes exactly, and no arithmetic touches the float.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

# Manual 3: PIX is paid in full and gives 5% off the list price.
PIX_DISCOUNT_PERCENT = Decimal("5")

# Manual 3.1: payment methods may be combined above this amount.
COMBINED_PAYMENT_THRESHOLD = Decimal("2000.00")

# Manual 3.1: minimum value per installment, by band. Up to 3x the manual sets no
# minimum beyond a R$ 50.00 floor on the installment itself.
INSTALLMENT_BANDS: tuple[tuple[int, int, Decimal], ...] = (
    (1, 3, Decimal("50.00")),
    (4, 6, Decimal("80.00")),
    (7, 12, Decimal("100.00")),
)

CENTS = Decimal("0.01")


def money(value: Decimal | str | int) -> Decimal:
    """Round to cents, half up, the way a till does."""
    return Decimal(value).quantize(CENTS, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class ProductPrice:
    product_id: int
    list_price: Decimal
    discount_percent: Decimal | None
    promotion_name: str | None
    final_price: Decimal
    pix_price: Decimal
    pix_discount_applies: bool
    max_installments: int
    installment_value: Decimal
    allows_combined_payment: bool


def _minimum_installment_for(count: int) -> Decimal:
    for low, high, minimum in INSTALLMENT_BANDS:
        if low <= count <= high:
            return minimum
    raise ValueError(f"{count} installments is outside the bands the store offers")


def max_installments(amount: Decimal) -> tuple[int, Decimal]:
    """Largest number of installments whose value clears its band's minimum.

    The bands are not monotonic: an amount can qualify for 4x and fail 5x, so
    every count is checked from the top down instead of assuming a cutoff.
    """
    highest = INSTALLMENT_BANDS[-1][1]
    for count in range(highest, 1, -1):
        value = money(amount / count)
        if value >= _minimum_installment_for(count):
            return count, value
    return 1, money(amount)


def _active_promotion(conn: sqlite3.Connection, product_id: int) -> sqlite3.Row | None:
    """Best active promotion for the product, or None.

    Manual 6.2: promotions are not cumulative. When more than one is running,
    the largest discount wins rather than the sum of them.
    """
    return conn.execute(
        """SELECT discount_percent, description
           FROM promotions
           WHERE product_id = ? AND is_active = 1
           ORDER BY discount_percent DESC
           LIMIT 1""",
        (product_id,),
    ).fetchone()


def price_for_product(conn: sqlite3.Connection, product_id: int) -> ProductPrice:
    row = conn.execute(
        "SELECT price_brl FROM products WHERE product_id = ?", (product_id,)
    ).fetchone()
    if row is None:
        raise LookupError(f"product {product_id} is not in the catalogue")

    list_price = money(str(row["price_brl"]))
    promotion = _active_promotion(conn, product_id)

    if promotion is None:
        discount_percent = None
        promotion_name = None
        final_price = list_price
    else:
        discount_percent = Decimal(str(promotion["discount_percent"]))
        promotion_name = promotion["description"]
        final_price = money(list_price * (Decimal(100) - discount_percent) / Decimal(100))

    # Manual 6.2: the PIX discount does not apply on an already promotional price.
    pix_discount_applies = promotion is None
    if pix_discount_applies:
        pix_price = money(
            final_price * (Decimal(100) - PIX_DISCOUNT_PERCENT) / Decimal(100)
        )
    else:
        pix_price = final_price

    # Installments are calculated on what the customer pays, not on the list price.
    count, value = max_installments(final_price)

    return ProductPrice(
        product_id=product_id,
        list_price=list_price,
        discount_percent=discount_percent,
        promotion_name=promotion_name,
        final_price=final_price,
        pix_price=pix_price,
        pix_discount_applies=pix_discount_applies,
        max_installments=count,
        installment_value=value,
        allows_combined_payment=final_price > COMBINED_PAYMENT_THRESHOLD,
    )
