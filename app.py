"""Streamlit interface: the conversation on the left, what the agent did on the right.

The trace panel is a development tool. A real customer on WhatsApp would see
only the left side. It is here because the brief asks the agent to decide when
to look at data and when to look at policy, and this makes that decision
visible instead of something the reader has to take on trust.
"""

from __future__ import annotations

import json

import streamlit as st
from openai import OpenAI

from emporio import config
from emporio.agent import Agent
from emporio.db import build_database

EXAMPLES = [
    "Quais opções de violões disponíveis custando até R$1000?",
    "Quanto custa o Takamine GD20?",
    "Qual o endereço e o horário da loja?",
    "Vocês têm saxofone?",
    "Me arrependi da compra, posso devolver o pedido 7?",
]

st.set_page_config(page_title="Tom · Empório da Música", layout="wide")


def md(text: str) -> str:
    """Escape the currency sign before Streamlit reads it as maths.

    Streamlit renders $...$ as LaTeX, so "R$ 429,90 e R$ 408,41 no PIX" comes
    out with the middle in italics and the figures mangled. Prices are the whole
    point of most answers here.
    """
    return text.replace("$", r"\$")


@st.cache_resource
def get_agent() -> Agent:
    client = OpenAI(api_key=config.api_key(), timeout=90.0)
    return Agent(build_database(same_thread=False), client, model=config.model_name())


def summarize(call: dict) -> str:
    """One line saying what came back, so the panel stays readable."""
    if call["error"]:
        return "erro"

    result = call["result"]
    if not isinstance(result, dict):
        return f"{len(result)} itens" if isinstance(result, list) else "ok"

    if "total_found" in result:
        return f"{result['total_found']} encontrados, {result['showing']} exibidos"
    if "products" in result:
        return f"{len(result['products'])} produto(s)"
    if "order" in result:
        return f"pedido {result['order']['order_id']}, {result['order']['status']}"
    if result.get("found") is False:
        return "nada encontrado"
    if "number" in result:
        return f"seção {result['number']}"
    return "ok"


def render_trace(turn: dict) -> None:
    st.markdown(md(f"**{turn['question']}**"))

    if not turn["calls"]:
        st.caption("Respondeu sem consultar nada.")
        return

    for call in turn["calls"]:
        arguments = ", ".join(f"{k}={v!r}" for k, v in call["arguments"].items())
        st.markdown(md(f"`{call['name']}({arguments})`"))
        st.caption(summarize(call))
        with st.expander("ver o que a ferramenta devolveu"):
            st.code(
                call["error"]
                or json.dumps(call["result"], ensure_ascii=False, indent=2),
                "text" if call["error"] else "json",
            )


def main() -> None:
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("turns", [])
    st.session_state.setdefault("pending", None)

    with st.sidebar:
        st.subheader("Tom")
        st.caption("Atendimento da Empório da Música, Campo Grande/MS.")
        st.divider()
        st.caption(f"Modelo: `{config.model_name()}`")
        st.caption(f"Data de referência: `{config.today()}`")
        st.divider()
        st.caption("Experimente")
        for index, example in enumerate(EXAMPLES):
            if st.button(example, key=f"ex{index}", use_container_width=True):
                st.session_state.pending = example
        st.divider()
        if st.button("Limpar conversa", use_container_width=True):
            st.session_state.history = []
            st.session_state.turns = []
            st.rerun()

    chat_column, trace_column = st.columns([3, 2], gap="large")

    with chat_column:
        st.subheader("Conversa")
        for message in st.session_state.history:
            with st.chat_message(message["role"]):
                st.markdown(md(message["content"]))

    with trace_column:
        st.subheader("O que o Tom consultou")
        st.caption(
            "Painel de desenvolvimento. O cliente não vê esta coluna."
        )
        if not st.session_state.turns:
            st.caption("Nada ainda.")
        for turn in reversed(st.session_state.turns):
            render_trace(turn)
            st.divider()

    question = st.chat_input("Escreva como você escreveria no WhatsApp") or (
        st.session_state.pending
    )
    if not question:
        return

    st.session_state.pending = None
    st.session_state.history.append({"role": "user", "content": question})

    with chat_column, st.chat_message("user"):
        st.markdown(md(question))

    with chat_column, st.chat_message("assistant"), st.spinner("Consultando..."):
        result = get_agent().respond(st.session_state.history)
        st.markdown(md(result.reply))

    st.session_state.history.append({"role": "assistant", "content": result.reply})
    st.session_state.turns.append(
        {
            "question": question,
            "calls": [
                {
                    "name": call.name,
                    "arguments": call.arguments,
                    "result": call.result,
                    "error": call.error,
                }
                for call in result.tool_calls
            ],
        }
    )
    st.rerun()


try:
    main()
except RuntimeError as error:
    st.error(str(error))
    st.caption("Copie `.env.example` para `.env` e preencha a chave da OpenAI.")
