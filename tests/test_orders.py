"""Order lookup and the identity check that guards it.

The check lives in the function, not in the prompt, so no conversation can talk
its way past it. Decision D-06 and conflict B-10 in docs/BUSINESS_RULES.md.
"""

from decimal import Decimal

import pytest

from emporio.db import build_database
from emporio.orders import get_order_status

# Order 3 belongs to Isabela Moreira Cunha, delivered, R$ 3450.00.
ORDER = 3
PHONE = "(67) 99678-9012"
EMAIL = "isabela.moreira@jmail.com"

# Order 20 belongs to a different customer and was cancelled.
CANCELLED_ORDER = 20
CANCELLED_PHONE = "(67) 98321-6543"
CANCELLED_EMAIL = "thiago.barbosa@jmail.com"


@pytest.fixture
def db():
    connection = build_database()
    yield connection
    connection.close()


def test_order_is_returned_when_phone_and_email_both_match(db):
    order = get_order_status(db, ORDER, phone=PHONE, email=EMAIL)

    assert order is not None
    assert order.status == "delivered"
    assert order.tracking_code == "BRDZ4561230BR"
    assert order.customer_name == "Isabela Moreira Cunha"


def test_a_wrong_phone_gets_nothing(db):
    """Knowing the order number and the email is not enough."""
    order = get_order_status(db, ORDER, phone="(67) 90000-0000", email=EMAIL)

    assert order is None


def test_a_wrong_email_gets_nothing(db):
    order = get_order_status(db, ORDER, phone=PHONE, email="outra.pessoa@jmail.com")

    assert order is None


def test_another_customers_credentials_do_not_open_this_order(db):
    """Real credentials, wrong order. This is the attack the check exists for."""
    order = get_order_status(
        db, ORDER, phone=CANCELLED_PHONE, email=CANCELLED_EMAIL
    )

    assert order is None


def test_an_order_that_does_not_exist_looks_the_same_as_a_failed_check(db):
    """B-10: the answer must not reveal which order numbers are real.

    If a missing order behaved differently from a wrong credential, anyone could
    sweep order numbers and learn which ones exist.
    """
    missing = get_order_status(db, 9999, phone=PHONE, email=EMAIL)
    refused = get_order_status(db, ORDER, phone="(67) 90000-0000", email=EMAIL)

    assert missing is None
    assert refused is None


def test_the_customer_may_type_the_phone_any_way_they_like(db):
    """Nobody types the punctuation the same way twice."""
    order = get_order_status(db, ORDER, phone="67996789012", email=EMAIL)

    assert order is not None


def test_the_email_is_not_case_sensitive(db):
    order = get_order_status(db, ORDER, phone=PHONE, email="Isabela.Moreira@Jmail.com")

    assert order is not None


def test_the_stored_total_is_reported_never_recalculated(db):
    """B-04: order 3 is stored at R$ 3450.00 while its items add up to R$ 3498.00.

    The customer paid the stored amount, so that is the only number to quote.
    """
    order = get_order_status(db, ORDER, phone=PHONE, email=EMAIL)

    assert order.total == Decimal("3450.00")
    assert sum(item.quantity for item in order.items) == 2


def test_a_cancelled_order_carries_the_reason(db):
    order = get_order_status(
        db, CANCELLED_ORDER, phone=CANCELLED_PHONE, email=CANCELLED_EMAIL
    )

    assert order.status == "cancelled"
    assert order.notes == "Endereço de entrega inválido informado pelo cliente"
    assert order.tracking_code is None


# Order 7 was placed on 2026-02-03 and delivered on 2026-02-17.
DELIVERED_ORDER = 7
DELIVERED_PHONE = "(67) 99789-0123"
DELIVERED_EMAIL = "leticia.rocha@jmail.com"


def _order7(db):
    return get_order_status(
        db, DELIVERED_ORDER, phone=DELIVERED_PHONE, email=DELIVERED_EMAIL
    )


def test_deadlines_are_calculated_in_code_not_by_the_model(monkeypatch, db):
    """D-14: the agent must never work out whether a window is still open.

    Three days after delivery, all three windows are open.
    """
    monkeypatch.setenv("EMPORIO_TODAY", "2026-02-20")

    deadlines = _order7(db).deadlines

    assert deadlines.received_on == "2026-02-17"
    assert deadlines.withdrawal_deadline == "2026-02-24"  # manual 4.1, 7 days
    assert deadlines.withdrawal_open is True
    assert deadlines.defect_exchange_deadline == "2026-03-05"  # manual 4.2, 30 days
    assert deadlines.defect_exchange_open is True
    assert deadlines.legal_warranty_until == "2026-05-18"  # manual 8.1, 90 days
    assert deadlines.legal_warranty_open is True


def test_an_expired_window_is_reported_as_expired(monkeypatch, db):
    """The answer to "can I return it?" months later is a date, not a maybe."""
    monkeypatch.setenv("EMPORIO_TODAY", "2026-11-02")

    deadlines = _order7(db).deadlines

    assert deadlines.withdrawal_open is False
    assert deadlines.withdrawal_deadline == "2026-02-24"
    assert deadlines.legal_warranty_open is False


def test_the_last_day_of_the_window_still_counts(monkeypatch, db):
    """Seven calendar days after delivery is inside the window, not outside."""
    monkeypatch.setenv("EMPORIO_TODAY", "2026-02-24")

    assert _order7(db).deadlines.withdrawal_open is True


def test_an_order_not_yet_delivered_has_no_deadlines_to_report(db):
    """Order 13 is pending, so nothing has been received and nothing has started."""
    customer = db.execute(
        "SELECT phone, email FROM customers WHERE customer_id = "
        "(SELECT customer_id FROM orders WHERE order_id = 13)"
    ).fetchone()

    order = get_order_status(db, 13, phone=customer["phone"], email=customer["email"])

    assert order.deadlines.received_on is None
    assert order.deadlines.withdrawal_open is False


def _credentials(db, order_id):
    row = db.execute(
        "SELECT phone, email FROM customers WHERE customer_id = "
        "(SELECT customer_id FROM orders WHERE order_id = ?)",
        (order_id,),
    ).fetchone()
    return {"phone": row["phone"], "email": row["email"]}


def test_a_shipped_order_has_not_been_received_yet(db):
    """Order 8 is shipped and carries an estimated delivery of 2026-02-28.

    B-11 uses the estimated delivery as the receipt date, which only holds for
    an order that arrived. Order 8 is the one order in this base that has the
    estimate without the delivery, so it is the one that proves the guard: drop
    it and this order starts reporting a return window counted from a delivery
    that never happened.
    """
    order = get_order_status(db, 8, **_credentials(db, 8))

    assert order.status == "shipped"
    assert order.estimated_delivery == "2026-02-28"
    assert order.deadlines.received_on is None
    assert order.deadlines.withdrawal_deadline is None


def test_a_cancelled_order_has_no_exchange_window(db):
    """Manual 4.2 counts thirty days from the purchase, for a faulty product.

    Order 20 was cancelled, so no product reached the customer and there is
    nothing to exchange. The window used to be reported open, and the persona
    tells the agent to state the date it finds.
    """
    order = get_order_status(db, CANCELLED_ORDER, **_credentials(db, CANCELLED_ORDER))

    assert order.status == "cancelled"
    assert order.deadlines.defect_exchange_deadline is None
    assert order.deadlines.defect_exchange_open is False


def test_an_undelivered_order_has_no_exchange_window_either(db):
    """Same rule, for an order still being prepared: order 13 is pending."""
    order = get_order_status(db, 13, **_credentials(db, 13))

    assert order.deadlines.defect_exchange_open is False
