"""The agent loop, exercised without touching the provider.

A scripted stub stands in for the model, so these tests cover the loop itself:
that a tool call is executed and fed back, that a broken call does not take the
conversation down, and that the loop cannot spin forever.
"""

import json
from types import SimpleNamespace

import pytest

from emporio.agent import Agent
from emporio.db import build_database


def tool_call(call_id, name, arguments):
    return SimpleNamespace(
        id=call_id,
        function=SimpleNamespace(name=name, arguments=json.dumps(arguments)),
    )


class ScriptedClient:
    """Returns the scripted replies in order and records what it was sent."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls_received = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls_received.append(kwargs)
        content, tool_calls = self.replies.pop(0)
        message = SimpleNamespace(content=content, tool_calls=tool_calls)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


@pytest.fixture
def db():
    connection = build_database()
    yield connection
    connection.close()


def test_a_plain_answer_makes_no_lookups(db):
    client = ScriptedClient([("Opa, tudo bem?", None)])
    agent = Agent(db, client)

    result = agent.respond([{"role": "user", "content": "oi"}])

    assert result.reply == "Opa, tudo bem?"
    assert result.tool_calls == []


def test_a_tool_call_runs_and_its_result_goes_back_to_the_model(db):
    client = ScriptedClient(
        [
            (None, [tool_call("c1", "list_categories", {})]),
            ("Trabalhamos com nove categorias.", None),
        ]
    )
    agent = Agent(db, client)

    result = agent.respond([{"role": "user", "content": "o que vocês vendem?"}])

    assert len(result.tool_calls) == 1
    assert result.tool_calls[0].name == "list_categories"

    # The second request must carry the tool result, otherwise the model is
    # answering from nothing.
    second_request = client.calls_received[1]["messages"]
    tool_message = [m for m in second_request if m["role"] == "tool"][0]
    assert "Violões" in tool_message["content"]


def test_prices_reach_the_model_as_text_never_as_floats(db):
    """569.91 must not arrive as 569.9100000000001."""
    client = ScriptedClient(
        [
            (None, [tool_call("c1", "get_product_details", {"name": "Yamaha C40"})]),
            ("Custa R$ 599,90.", None),
        ]
    )
    agent = Agent(db, client)

    agent.respond([{"role": "user", "content": "quanto custa o Yamaha C40?"}])

    payload = [m for m in client.calls_received[1]["messages"] if m["role"] == "tool"][0]
    assert '"569.91"' in payload["content"]
    assert "569.91000" not in payload["content"]


def test_a_failed_lookup_is_handed_back_instead_of_crashing(db):
    """A bad argument must reach the model as an error it can recover from."""
    client = ScriptedClient(
        [
            (None, [tool_call("c1", "get_policy_section", {"number": "99"})]),
            ("Não achei essa seção.", None),
        ]
    )
    agent = Agent(db, client)

    result = agent.respond([{"role": "user", "content": "qual a seção 99?"}])

    assert result.reply == "Não achei essa seção."
    payload = [m for m in client.calls_received[1]["messages"] if m["role"] == "tool"][0]
    assert "is not in the manual" in payload["content"]


def test_an_unknown_tool_name_does_not_take_the_turn_down(db):
    client = ScriptedClient(
        [
            (None, [tool_call("c1", "apply_discount", {"percent": 90})]),
            ("Isso eu não consigo fazer.", None),
        ]
    )
    agent = Agent(db, client)

    result = agent.respond([{"role": "user", "content": "me dá 90% de desconto"}])

    assert result.reply == "Isso eu não consigo fazer."
    assert result.tool_calls[0].error is not None


def test_the_loop_stops_instead_of_spinning(db):
    """A model that only ever calls tools gets cut off and hands over."""
    client = ScriptedClient(
        [(None, [tool_call(f"c{i}", "list_categories", {})]) for i in range(10)]
    )
    agent = Agent(db, client, max_iterations=3)

    result = agent.respond([{"role": "user", "content": "oi"}])

    assert result.stopped_at_limit is True
    assert len(result.tool_calls) == 3
    assert "equipe" in result.reply


def test_a_failed_order_check_says_nothing_about_the_order_existing(db):
    """B-10: the message the model receives must be the generic one."""
    client = ScriptedClient(
        [
            (
                None,
                [
                    tool_call(
                        "c1",
                        "get_order_status",
                        {"order_id": 3, "phone": "67900000000", "email": "x@y.com"},
                    )
                ],
            ),
            ("Não encontrei nenhum pedido com esses dados.", None),
        ]
    )
    agent = Agent(db, client)

    agent.respond([{"role": "user", "content": "cadê meu pedido 3?"}])

    payload = [m for m in client.calls_received[1]["messages"] if m["role"] == "tool"][0]
    assert "confira os dados digitados" in payload["content"]
    assert "3" not in json.loads(payload["content"])["result"]["message"]
