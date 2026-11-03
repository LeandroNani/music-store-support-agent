"""In-memory database built from the original CSVs.

The files in data/raw are read and never written to. The database lives only
as long as the process, and is rebuilt every time the application starts.
"""

from __future__ import annotations

import csv
import re
import sqlite3
import unicodedata
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

SCHEMA = """
CREATE TABLE categories (
    category_id  INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    description  TEXT
);

CREATE TABLE products (
    product_id      INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    category_id     INTEGER REFERENCES categories(category_id),
    price_brl       REAL NOT NULL,
    description     TEXT,
    stock_quantity  INTEGER NOT NULL,
    status          TEXT NOT NULL,
    specs           TEXT,
    created_at      TEXT
);

CREATE TABLE customers (
    customer_id   INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    phone         TEXT,
    phone_digits  TEXT,
    email         TEXT,
    email_norm    TEXT,
    city          TEXT
);

CREATE TABLE orders (
    order_id            INTEGER PRIMARY KEY,
    customer_id         INTEGER REFERENCES customers(customer_id),
    order_date          TEXT NOT NULL,
    status              TEXT NOT NULL,
    total_brl           REAL NOT NULL,
    payment_method      TEXT,
    tracking_code       TEXT,
    estimated_delivery  TEXT,
    notes               TEXT
);

CREATE TABLE order_items (
    order_id    INTEGER REFERENCES orders(order_id),
    product_id  INTEGER REFERENCES products(product_id),
    quantity    INTEGER NOT NULL
);

CREATE TABLE promotions (
    promotion_id      INTEGER PRIMARY KEY,
    product_id        INTEGER REFERENCES products(product_id),
    discount_percent  REAL NOT NULL,
    description       TEXT,
    is_active         INTEGER NOT NULL
);

CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_promotions_product ON promotions(product_id, is_active);
CREATE INDEX idx_order_items_order ON order_items(order_id);
"""


def normalize_text(value: str | None) -> str | None:
    """Unicode NFC, and trim the ends.

    The CSVs carry "Ponta Porã" in two different Unicode forms, which makes two
    identical city names fail to match.
    """
    if value is None:
        return None
    cleaned = unicodedata.normalize("NFC", value).strip()
    return cleaned or None


def digits_only(value: str | None) -> str | None:
    """Phone reduced to digits, to compare with whatever the customer types."""
    if not value:
        return None
    return re.sub(r"\D", "", value) or None


def normalize_email(value: str | None) -> str | None:
    cleaned = normalize_text(value)
    return cleaned.lower() if cleaned else None


def _fold_for_sql(value: str | None) -> str:
    """Lowercase without accents, exposed to SQL as fold()."""
    if value is None:
        return ""
    decomposed = unicodedata.normalize("NFD", value)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def _read_csv(name: str) -> list[dict[str, str | None]]:
    path = DATA_DIR / name
    with path.open(encoding="utf-8", newline="") as handle:
        return [
            {key: normalize_text(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def build_database(same_thread: bool = True) -> sqlite3.Connection:
    """Build the in-memory database and return the connection.

    Streamlit may re-run the script on a different thread between one message
    and the next, while the connection stays in the session, which is why the
    interface passes same_thread=False.
    """
    conn = sqlite3.connect(":memory:", check_same_thread=same_thread)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)

    # SQLite compares accents literally, so "eletrico" would not find "Elétrico".
    conn.create_function("fold", 1, _fold_for_sql, deterministic=True)

    conn.executemany(
        "INSERT INTO categories VALUES (:category_id, :name, :description)",
        [
            {
                "category_id": int(r["category_id"]),
                "name": r["name"],
                "description": r["description"],
            }
            for r in _read_csv("categories.csv")
        ],
    )

    conn.executemany(
        """INSERT INTO products VALUES (:product_id, :name, :category_id, :price_brl,
           :description, :stock_quantity, :status, :specs, :created_at)""",
        [
            {
                "product_id": int(r["product_id"]),
                "name": r["name"],
                "category_id": int(r["category_id"]),
                "price_brl": float(r["price_brl"]),
                "description": r["description"],
                "stock_quantity": int(r["stock_quantity"]),
                "status": r["status"],
                "specs": r["specs"],
                "created_at": r["created_at"],
            }
            for r in _read_csv("products.csv")
        ],
    )

    conn.executemany(
        """INSERT INTO customers VALUES (:customer_id, :name, :phone, :phone_digits,
           :email, :email_norm, :city)""",
        [
            {
                "customer_id": int(r["customer_id"]),
                "name": r["name"],
                "phone": r["phone"],
                "phone_digits": digits_only(r["phone"]),
                "email": r["email"],
                "email_norm": normalize_email(r["email"]),
                "city": r["city"],
            }
            for r in _read_csv("customers.csv")
        ],
    )

    conn.executemany(
        """INSERT INTO orders VALUES (:order_id, :customer_id, :order_date, :status,
           :total_brl, :payment_method, :tracking_code, :estimated_delivery, :notes)""",
        [
            {
                "order_id": int(r["order_id"]),
                "customer_id": int(r["customer_id"]),
                "order_date": r["order_date"],
                "status": r["status"],
                "total_brl": float(r["total_brl"]),
                "payment_method": r["payment_method"],
                "tracking_code": r["tracking_code"],
                "estimated_delivery": r["estimated_delivery"],
                "notes": r["notes"],
            }
            for r in _read_csv("orders.csv")
        ],
    )

    conn.executemany(
        "INSERT INTO order_items VALUES (:order_id, :product_id, :quantity)",
        [
            {
                "order_id": int(r["order_id"]),
                "product_id": int(r["product_id"]),
                "quantity": int(r["quantity"]),
            }
            for r in _read_csv("order_items.csv")
        ],
    )

    conn.executemany(
        """INSERT INTO promotions VALUES (:promotion_id, :product_id, :discount_percent,
           :description, :is_active)""",
        [
            {
                "promotion_id": int(r["promotion_id"]),
                "product_id": int(r["product_id"]),
                "discount_percent": float(r["discount_percent"]),
                "description": r["description"],
                "is_active": int(r["is_active"]),
            }
            for r in _read_csv("promotions.csv")
        ],
    )

    conn.commit()
    return conn


if __name__ == "__main__":
    connection = build_database()
    tables = [
        "categories",
        "products",
        "customers",
        "orders",
        "order_items",
        "promotions",
    ]
    for table in tables:
        count = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table:<13} {count:>4}")
