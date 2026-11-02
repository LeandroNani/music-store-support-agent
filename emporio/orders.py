"""Order lookup, guarded by an identity check.

The check is a required parameter of the function, not an instruction in the
prompt. A conversation cannot argue its way past a WHERE clause: the model never
receives an order it was not entitled to, so there is nothing for it to leak.

Decision D-06 covers the reasoning, conflict B-10 covers which fields are asked
for and what this check cannot do without a real WhatsApp channel.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from emporio.config import today
from emporio.db import digits_only, normalize_email
from emporio.pricing import money

# Manual 4.1: seven calendar days from receipt to change your mind.
WITHDRAWAL_DAYS = 7
# Manual 4.2: thirty calendar days from the purchase for a manufacturing fault.
DEFECT_EXCHANGE_DAYS = 30
# Manual 8.1: ninety days of legal warranty, counted from receipt.
LEGAL_WARRANTY_DAYS = 90


@dataclass(frozen=True)
class OrderItem:
    product_id: int
    product_name: str
    quantity: int


@dataclass(frozen=True)
class Deadlines:
    """Which windows are still open on this order, worked out in code.

    The model is told the answer, never the arithmetic. Decision D-14 keeps
    every calculation out of the model, and D-11 is why the reference date
    comes from config.today() and can be pinned for a reproducible example.

    The dataset has no actual delivery date, only the estimated one, so that
    is what the windows are counted from. Recorded in BUSINESS_RULES as B-11.
    """

    received_on: str | None
    withdrawal_deadline: str | None
    withdrawal_open: bool
    defect_exchange_deadline: str | None
    defect_exchange_open: bool
    legal_warranty_until: str | None
    legal_warranty_open: bool


def _deadlines(order_date: str, received_on: str | None) -> Deadlines:
    now = today()

    purchase = date.fromisoformat(order_date)
    defect_limit = purchase + timedelta(days=DEFECT_EXCHANGE_DAYS)

    if received_on is None:
        # Nothing was received, so no window counted from receipt has started.
        return Deadlines(
            received_on=None,
            withdrawal_deadline=None,
            withdrawal_open=False,
            defect_exchange_deadline=defect_limit.isoformat(),
            defect_exchange_open=now <= defect_limit,
            legal_warranty_until=None,
            legal_warranty_open=False,
        )

    received = date.fromisoformat(received_on)
    withdrawal_limit = received + timedelta(days=WITHDRAWAL_DAYS)
    warranty_limit = received + timedelta(days=LEGAL_WARRANTY_DAYS)

    return Deadlines(
        received_on=received_on,
        withdrawal_deadline=withdrawal_limit.isoformat(),
        withdrawal_open=now <= withdrawal_limit,
        defect_exchange_deadline=defect_limit.isoformat(),
        defect_exchange_open=now <= defect_limit,
        legal_warranty_until=warranty_limit.isoformat(),
        legal_warranty_open=now <= warranty_limit,
    )


@dataclass(frozen=True)
class Order:
    order_id: int
    customer_name: str
    status: str
    order_date: str
    total: Decimal
    payment_method: str | None
    tracking_code: str | None
    estimated_delivery: str | None
    notes: str | None
    items: list[OrderItem]
    deadlines: Deadlines


def get_order_status(
    conn: sqlite3.Connection,
    order_id: int,
    phone: str,
    email: str,
) -> Order | None:
    """The order, or None when the caller has not proved it is theirs.

    None covers both "no such order" and "those details do not match", on
    purpose. Telling the two apart would let anyone sweep order numbers and
    learn which ones exist, the same reason a login does not say whether it was
    the user or the password that was wrong.

    The phone is compared digit by digit and the email case-insensitively, so
    the customer is not punished for typing the punctuation differently.
    """
    row = conn.execute(
        """SELECT o.*, c.name AS customer_name
           FROM orders o
           JOIN customers c ON c.customer_id = o.customer_id
           WHERE o.order_id = ?
             AND c.phone_digits = ?
             AND c.email_norm = ?""",
        (order_id, digits_only(phone), normalize_email(email)),
    ).fetchone()

    if row is None:
        return None

    items = conn.execute(
        """SELECT i.product_id, i.quantity, p.name
           FROM order_items i
           JOIN products p ON p.product_id = i.product_id
           WHERE i.order_id = ?""",
        (order_id,),
    ).fetchall()

    return Order(
        order_id=row["order_id"],
        customer_name=row["customer_name"],
        status=row["status"],
        order_date=row["order_date"],
        # B-04: two orders in this dataset are stored with a total that differs
        # from the sum of their items. The stored value is what was charged.
        total=money(str(row["total_brl"])),
        payment_method=row["payment_method"],
        tracking_code=row["tracking_code"],
        estimated_delivery=row["estimated_delivery"],
        notes=row["notes"],
        # Only a delivered order has been received. The dataset carries the
        # estimated delivery date, which is the closest thing it has to one.
        deadlines=_deadlines(
            row["order_date"],
            row["estimated_delivery"] if row["status"] == "delivered" else None,
        ),
        items=[
            OrderItem(
                product_id=item["product_id"],
                product_name=item["name"],
                quantity=item["quantity"],
            )
            for item in items
        ],
    )
