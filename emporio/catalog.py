"""Catalogue lookups, with the store's rules already applied.

Nothing here hands the model a raw row. Prices arrive final, availability
arrives as a flag, and products the store no longer offers never show up in a
search. See docs/BUSINESS_RULES.md for where each rule comes from.
"""

from __future__ import annotations

import json
import sqlite3
import unicodedata
from dataclasses import dataclass, field
from decimal import Decimal

from emporio.pricing import ProductPrice, price_for_product

DEFAULT_PAGE_SIZE = 10


def fold(value: str | None) -> str:
    """Lowercase without accents, so "eletrico" finds "Elétrico"."""
    if value is None:
        return ""
    decomposed = unicodedata.normalize("NFD", value)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


@dataclass(frozen=True)
class Category:
    category_id: int
    name: str
    description: str
    product_count: int


@dataclass(frozen=True)
class ProductSummary:
    product_id: int
    name: str
    category: str
    price: ProductPrice
    stock_quantity: int
    status: str
    fits_budget_only_with_pix: bool = False

    @property
    def in_stock(self) -> bool:
        return self.stock_quantity > 0

    @property
    def discontinued(self) -> bool:
        return self.status == "discontinued"

    @property
    def coming_soon(self) -> bool:
        return self.status == "coming_soon"


@dataclass(frozen=True)
class ProductDetails(ProductSummary):
    description: str = ""
    specs: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchResult:
    total: int
    offset: int
    items: list[ProductSummary]

    @property
    def has_more(self) -> bool:
        return self.offset + len(self.items) < self.total


def list_categories(conn: sqlite3.Connection) -> list[Category]:
    """Every category with how many products it holds.

    The count matters: three categories in this catalogue have none, and the
    agent has to say the store works with them but has nothing in stock (B-05).
    """
    rows = conn.execute(
        """SELECT c.category_id, c.name, c.description, COUNT(p.product_id) AS n
           FROM categories c
           LEFT JOIN products p ON p.category_id = c.category_id
           GROUP BY c.category_id, c.name, c.description
           ORDER BY c.category_id"""
    ).fetchall()
    return [
        Category(r["category_id"], r["name"], r["description"], r["n"]) for r in rows
    ]


def _specs(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _matches_specs(
    specs: dict[str, str], strings: str | None, electronics: bool | None
) -> bool:
    if strings is not None and fold(specs.get("strings")) != fold(strings):
        return False
    if electronics is not None:
        has_electronics = fold(specs.get("electronics")) in {"yes", "sim"}
        if has_electronics != electronics:
            return False
    return True


def search_products(
    conn: sqlite3.Connection,
    query: str | None = None,
    category: str | int | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    strings: str | None = None,
    electronics: bool | None = None,
    offset: int = 0,
    limit: int = DEFAULT_PAGE_SIZE,
) -> SearchResult:
    """Products matching the customer's request, cheapest first.

    Discontinued products are left out, because they are no longer part of the
    catalogue the store offers (B-01). Out of stock products stay in, flagged,
    because they are still part of it (B-03).

    The price filter uses the lowest amount the customer can actually pay, so a
    product that only fits the budget on PIX is listed and marked as such (B-09).
    """
    sql = ["SELECT p.*, c.name AS category_name FROM products p",
           "LEFT JOIN categories c ON c.category_id = p.category_id",
           "WHERE p.status <> 'discontinued'"]
    params: list[object] = []

    if query:
        sql.append("AND fold(p.name) LIKE ?")
        params.append(f"%{fold(query)}%")

    if isinstance(category, int):
        sql.append("AND p.category_id = ?")
        params.append(category)
    elif category:
        sql.append("AND fold(c.name) = ?")
        params.append(fold(category))

    rows = conn.execute(" ".join(sql), params).fetchall()

    matched: list[ProductSummary] = []
    for row in rows:
        specs = _specs(row["specs"])
        if not _matches_specs(specs, strings, electronics):
            continue

        price = price_for_product(conn, row["product_id"])
        cheapest = min(price.final_price, price.pix_price)

        if max_price is not None and cheapest > Decimal(max_price):
            continue
        if min_price is not None and cheapest < Decimal(min_price):
            continue

        matched.append(
            ProductSummary(
                product_id=row["product_id"],
                name=row["name"],
                category=row["category_name"],
                price=price,
                stock_quantity=row["stock_quantity"],
                status=row["status"],
                fits_budget_only_with_pix=(
                    max_price is not None and price.final_price > Decimal(max_price)
                ),
            )
        )

    matched.sort(key=lambda item: item.price.final_price)
    return SearchResult(
        total=len(matched),
        offset=offset,
        items=matched[offset : offset + limit],
    )


def get_product_details(
    conn: sqlite3.Connection,
    product_id: int | None = None,
    name: str | None = None,
    limit: int = 5,
) -> list[ProductDetails]:
    """One product by id, or every product whose name contains the text.

    Unlike the search, this does not hide discontinued products. A customer who
    asks for the Ibanez Bass 2X by name gets it, with the warning that it is a
    closed line, because the store still has units to sell (B-01).

    A list is returned rather than a single product so the agent can ask which
    one the customer meant instead of picking for them.
    """
    if product_id is None and not name:
        raise ValueError("pass either product_id or name")

    sql = ["SELECT p.*, c.name AS category_name FROM products p",
           "LEFT JOIN categories c ON c.category_id = p.category_id",
           "WHERE 1 = 1"]
    params: list[object] = []

    if product_id is not None:
        sql.append("AND p.product_id = ?")
        params.append(product_id)
    if name:
        sql.append("AND fold(p.name) LIKE ?")
        params.append(f"%{fold(name)}%")

    sql.append("ORDER BY p.price_brl LIMIT ?")
    params.append(limit)

    return [
        ProductDetails(
            product_id=row["product_id"],
            name=row["name"],
            category=row["category_name"],
            price=price_for_product(conn, row["product_id"]),
            stock_quantity=row["stock_quantity"],
            status=row["status"],
            description=row["description"] or "",
            specs=_specs(row["specs"]),
        )
        for row in conn.execute(" ".join(sql), params).fetchall()
    ]
