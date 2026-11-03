"""The agent loop.

A plain reason-and-act loop over the provider's native tool calling. The model
decides which lookup it needs, this code runs it, the result goes back, and the
loop repeats until the model answers in words. Decision D-01 covers why there
is no agent framework here.

Nothing in this file decides anything about the store. It routes, it executes,
and it records what happened so the interface can show it.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Callable

from emporio import catalog, orders, policies
from emporio.persona import build_system_prompt

DEFAULT_MODEL = "gpt-6-luna"

# A turn needs a handful of lookups at most. The cap exists so a confused model
# cannot sit in a loop spending tokens.
MAX_ITERATIONS = 6

# gpt-6-luna rejects function tools on /v1/chat/completions unless reasoning is
# turned off. Another model may not need this, so it is passed as options
# rather than hard-coded into the call.
DEFAULT_EXTRA_OPTIONS: dict[str, Any] = {"reasoning_effort": "none"}

NOT_FOUND_MESSAGE = (
    "Não encontrei nenhum pedido com esses dados, confira os dados digitados."
)


@dataclass(frozen=True)
class ToolCall:
    """One lookup the agent made, kept so the interface can display the trace."""

    name: str
    arguments: dict[str, Any]
    result: Any
    error: str | None = None


@dataclass
class TurnResult:
    reply: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    stopped_at_limit: bool = False


def _plain(value: Any) -> Any:
    """Make a result JSON-safe.

    Decimal becomes a string, never a float: the model must receive "569.91",
    not 569.9100000000001.
    """
    if isinstance(value, Decimal):
        return f"{value:.2f}"
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if hasattr(value, "__dataclass_fields__"):
        out = {name: _plain(getattr(value, name)) for name in value.__dataclass_fields__}
        # Dataclass properties carry the store's flags; they belong in the payload.
        for name in ("in_stock", "discontinued", "coming_soon", "has_more"):
            if hasattr(value, name):
                out[name] = getattr(value, name)
        return out
    return value


TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": (
                "Busca instrumentos no catálogo. Use quando o cliente procura "
                "um tipo de instrumento, uma faixa de preço ou uma característica, "
                "em vez de um modelo específico. Devolve no máximo 10 por página, "
                "junto com o total encontrado."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Texto que aparece no nome do produto.",
                    },
                    "category": {
                        "type": "string",
                        "description": (
                            "Nome exato da categoria, como aparece em "
                            "list_categories. Ex.: Violões, Ukuleles, Guitarras."
                        ),
                    },
                    "min_price": {"type": "number"},
                    "max_price": {"type": "number"},
                    "strings": {
                        "type": "string",
                        "description": "Tipo de corda: nylon ou aço.",
                    },
                    "electronics": {
                        "type": "boolean",
                        "description": "true para instrumento com captação.",
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Use 10 para a segunda página, 20 para a terceira.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_details",
            "description": (
                "Detalhe de um produto: preço de tabela, promoção ativa, preço no "
                "PIX, parcelamento, estoque e especificações. Use quando o cliente "
                "cita um modelo pelo nome. Pode devolver mais de um resultado, e aí "
                "pergunte ao cliente qual ele quer."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Parte do nome do produto."},
                    "product_id": {"type": "integer"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": (
                "Situação de um pedido. Exige o número do pedido mais o telefone e "
                "o e-mail cadastrados, os três juntos. Peça os dados ao cliente "
                "antes de chamar. Se não encontrar, não revele se o número existe."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "integer"},
                    "phone": {"type": "string"},
                    "email": {"type": "string"},
                },
                "required": ["order_id", "phone", "email"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_categories",
            "description": (
                "Categorias do catálogo e quantos produtos cada uma tem. Use para "
                "saber se a loja trabalha com um tipo de instrumento. A contagem "
                "não diz o que está em estoque: para isso use search_products."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_policy_section",
            "description": (
                "Texto de uma seção do manual de políticas da loja, pelo número. "
                "Use para troca, devolução, garantia, frete, formas de pagamento, "
                "horário e dados da loja. O índice está no prompt do sistema."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "number": {
                        "type": "string",
                        "description": 'Número da seção, como "4" ou "4.1".',
                    }
                },
                "required": ["number"],
            },
        },
    },
]


def _availability(item: catalog.ProductSummary) -> str:
    if item.coming_soon:
        return "em breve"
    return "em estoque" if item.in_stock else "fora de estoque"


def _search_item(item: catalog.ProductSummary) -> dict[str, Any]:
    """One line of a result list, trimmed to what a listing needs.

    Installments and specifications are left for get_product_details. Repeating
    them for every row makes the payload long enough that the model skims it,
    which is how an out of stock flag gets missed.
    """
    payload: dict[str, Any] = {
        "product_id": item.product_id,
        "name": item.name,
        "category": item.category,
        "price": f"{item.price.final_price:.2f}",
        "pix_price": f"{item.price.pix_price:.2f}",
        "availability": _availability(item),
    }
    if item.price.discount_percent is not None:
        payload["list_price"] = f"{item.price.list_price:.2f}"
        payload["discount_percent"] = f"{item.price.discount_percent:g}"
        payload["promotion"] = item.price.promotion_name
    if item.fits_budget_only_with_pix:
        payload["only_fits_budget_with_pix"] = True
    return payload


def _build_dispatch(conn: sqlite3.Connection) -> dict[str, Callable[..., Any]]:
    def search(**kwargs: Any) -> Any:
        for key in ("min_price", "max_price"):
            if kwargs.get(key) is not None:
                kwargs[key] = Decimal(str(kwargs[key]))
        result = catalog.search_products(conn, **kwargs)
        return {
            "total_found": result.total,
            "showing": len(result.items),
            "offset": result.offset,
            "has_more": result.has_more,
            "items": [_search_item(item) for item in result.items],
        }

    def details(**kwargs: Any) -> Any:
        found = catalog.get_product_details(conn, **kwargs)
        if not found:
            return {"found": False, "message": "Nenhum produto com esse nome."}
        return {"found": True, "products": found}

    def order(**kwargs: Any) -> Any:
        found = orders.get_order_status(conn, **kwargs)
        if found is None:
            # Same answer whether the order is missing or the details are wrong.
            return {"found": False, "message": NOT_FOUND_MESSAGE}
        return {"found": True, "order": found}

    def section(number: str) -> Any:
        try:
            return policies.get_section(number)
        except policies.PolicySectionNotFound as exc:
            return {"found": False, "message": str(exc)}

    return {
        "search_products": search,
        "get_product_details": details,
        "get_order_status": order,
        "list_categories": lambda: catalog.list_categories(conn),
        "get_policy_section": section,
    }


class Agent:
    def __init__(
        self,
        conn: sqlite3.Connection,
        client: Any,
        model: str = DEFAULT_MODEL,
        max_iterations: int = MAX_ITERATIONS,
        extra_options: dict[str, Any] | None = None,
    ) -> None:
        self.conn = conn
        self.client = client
        self.model = model
        self.max_iterations = max_iterations
        self.extra_options = (
            DEFAULT_EXTRA_OPTIONS if extra_options is None else extra_options
        )
        self.dispatch = _build_dispatch(conn)
        self.system_prompt = build_system_prompt()

    def _run_tool(self, name: str, raw_arguments: str) -> ToolCall:
        try:
            arguments = json.loads(raw_arguments) if raw_arguments else {}
        except json.JSONDecodeError as exc:
            return ToolCall(name, {}, None, error=f"argumentos inválidos: {exc}")

        handler = self.dispatch.get(name)
        if handler is None:
            return ToolCall(name, arguments, None, error=f"ferramenta {name} não existe")

        try:
            return ToolCall(name, arguments, _plain(handler(**arguments)))
        except Exception as exc:  # the model gets the error and can try again
            return ToolCall(name, arguments, None, error=f"{type(exc).__name__}: {exc}")

    def respond(self, history: list[dict[str, Any]]) -> TurnResult:
        """One customer turn: zero or more lookups, then an answer in words.

        `history` is the conversation so far, in the provider's message format,
        without the system prompt.
        """
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt},
            *history,
        ]
        trace: list[ToolCall] = []

        for _ in range(self.max_iterations):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOL_SCHEMAS,
                # gpt-6-luna refuses function tools on this endpoint unless
                # reasoning is off. Nothing is lost: the reasoning this agent
                # needs is which lookup to make, and the deliberation that the
                # parameter buys would be spent on work already done in Python.
                **self.extra_options,
            )
            message = response.choices[0].message

            if not getattr(message, "tool_calls", None):
                return TurnResult(reply=message.content or "", tool_calls=trace)

            messages.append(
                {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": "function",
                            "function": {
                                "name": call.function.name,
                                "arguments": call.function.arguments,
                            },
                        }
                        for call in message.tool_calls
                    ],
                }
            )

            for call in message.tool_calls:
                executed = self._run_tool(call.function.name, call.function.arguments)
                trace.append(executed)
                payload = (
                    {"error": executed.error}
                    if executed.error
                    else {"result": executed.result}
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": json.dumps(payload, ensure_ascii=False),
                    }
                )

        return TurnResult(
            reply=(
                "Desculpa, me embolei aqui. Pode repetir de outro jeito, "
                "ou prefere falar com alguém da equipe?"
            ),
            tool_calls=trace,
            stopped_at_limit=True,
        )
