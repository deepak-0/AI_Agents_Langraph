from __future__ import annotations

import asyncio
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.types import interrupt

from .config import CRIBL_MCP_URL, CRIBL_TOKEN

_cribl_tools: list[Any] | None = None
_cribl_tools_lock = asyncio.Lock()


async def get_cribl_tools() -> list[Any]:
    """Discover Cribl tools once per application process."""
    global _cribl_tools

    if _cribl_tools is not None:
        return _cribl_tools

    async with _cribl_tools_lock:
        # Another concurrent request may have populated the cache while waiting.
        if _cribl_tools is not None:
            return _cribl_tools

        client = MultiServerMCPClient(
            {
                "cribl": {
                    "url": CRIBL_MCP_URL,
                    "transport": "streamable_http",
                    "headers": {
                        "Authorization": f"Bearer {CRIBL_TOKEN}",
                        "Accept": "application/json, text/event-stream",
                    },
                }
            }
        )
        _cribl_tools = await client.get_tools()
        print(f"Available Cribl tools: {[tool.name for tool in _cribl_tools]}")
        return _cribl_tools


async def get_cribl_answer(llm: Any, question: str) -> str:
    if not CRIBL_TOKEN:
        return (
            "Cribl integration is not configured. Set the CRIBL_TOKEN environment variable "
            "before using the 'cribl' route."
        )

    tools = await get_cribl_tools()
    tools_by_name = {tool.name: tool for tool in tools}

    messages = [
        SystemMessage(content=(
            "You answer Cribl questions using the provided Cribl tools. "
            "Use only read-only tools. Give a concise summary of the returned data."
        )),
        HumanMessage(content=question),
    ]

    assistant_message = await llm.bind_tools(tools).ainvoke(messages)

    for tool_call in getattr(assistant_message, "tool_calls", []) or []:
        tool_name = tool_call["name"]
        tool = tools_by_name.get(tool_name)
        if tool is None:
            continue

        result = await tool.ainvoke(tool_call["args"])
        messages.extend(
            [
                assistant_message,
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                ),
            ]
        )
        assistant_message = await llm.bind_tools(tools).ainvoke(messages)

    return assistant_message.content
