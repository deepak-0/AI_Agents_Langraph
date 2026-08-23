from __future__ import annotations

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from .config import DEFAULT_MODEL
from .cribl import get_cribl_answer
from .llm import get_llm
from .prompts import CHAT_PROMPT, CLASSIFY_PROMPT, KQL_PROMPT, SUMMARY_PROMPT
from .state import State


def build_graph(model_name: str = DEFAULT_MODEL):
    llm = get_llm(model_name)

    def llm_classify(state: State) -> dict[str, str]:
        print(f"Classifying User Input: {state['user_input']}")
        messages = [
            SystemMessage(content=CLASSIFY_PROMPT),
            HumanMessage(content=state["user_input"]),
        ]
        resp = llm.invoke(messages)
        route = resp.content.strip().lower()
        if route not in ["kql", "chat", "cribl"]:
            route = "chat"
        return {"route": route}

    def chat_node(state: State) -> dict[str, str]:
        print(f"Processing chat input: {state['user_input']}")
        messages = [
            SystemMessage(content=CHAT_PROMPT),
            HumanMessage(content=state["user_input"]),
        ]
        resp = llm.invoke(messages)
        return {"output": resp.content}

    def kql_node(state: State) -> dict[str, str]:
        print(f"Processing KQL input: {state['user_input']}")
        messages = [
            SystemMessage(content=KQL_PROMPT),
            HumanMessage(content=state["user_input"]),
        ]
        resp = llm.invoke(messages)
        return {"output": resp.content}

    async def cribl_node(state: State) -> dict[str, str]:
        print(f"Processing Cribl input: {state['user_input']}")
        output = await get_cribl_answer(llm, state["user_input"])
        return {"output": output}

    def summary_node(state: State) -> dict[str, str]:
        print(f"Generating summary for output: {state['output']}")
        messages = [
            SystemMessage(content=SUMMARY_PROMPT),
            HumanMessage(content=state["output"]),
        ]
        resp = llm.invoke(messages)
        return {"summary": resp.content}
    
    builder = StateGraph(State)
    builder.add_node("classify", llm_classify)
    builder.add_node("chat", chat_node)
    builder.add_node("kql", kql_node)
    builder.add_node("cribl", cribl_node)
    builder.add_node("summary", summary_node)

    builder.set_entry_point("classify")
    builder.add_conditional_edges(
        "classify",
        lambda s: s["route"],
        {"kql": "kql", "chat": "chat", "cribl": "cribl"},
    )
    builder.add_edge("chat","summary")
    builder.add_edge("kql", "summary")
    builder.add_edge("cribl", "summary")
    builder.add_edge("summary", END)

    return builder.compile()
