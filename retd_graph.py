from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama

class State(TypedDict):
    user_input: str
    route: Literal["kql", "chat"]
    output: str

llm = ChatOllama(model="qwen2.5", temperature=0.2)

def classify(state: State) -> dict[str, str]:
    text = state["user_input"].lower()
    if "kql" in text:
        return {"route": "kql"}
    else:
        return {"route": "chat"}

def chat_node(state: State):
    prompt = ("You are a helpful assisitant that answers questions in a concise manner. ")
    resp = llm.invoke(prompt)
    return {"output": resp.content}
    
def kql_node(state: State):
    prompt = ("You are a Senior SOC detection engineer. You are an expert in writing KQL queries to detect security threats. Answer the question in a concise manner and provide only the KQL query as output.")
    resp = llm.invoke(prompt)
    return {"output": resp.content}
    
builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("chat", chat_node)
builder.add_node("kql", kql_node)

builder.set_entry_point("classify")

builder.add_conditional_edges(
    "classify", 
    lambda s: s["route"],
    {"kql": "kql", "chat": "chat"}
)
builder.add_edge("chat", END)
builder.add_edge("kql", END)
