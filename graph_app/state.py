from typing import Literal, TypedDict


class State(TypedDict):
    user_input: str
    route: Literal["kql", "chat", "cribl"]
    output: str
