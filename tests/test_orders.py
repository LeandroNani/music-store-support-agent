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
