from typing import TypedDict, Annotated, Literal
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
    intent: Literal[
        "register_expense",
        "get_expenses",
        "set_budget",
        "get_remaining_budget",
        "unknown"
    ]
    
    data: dict  # payload estruturado extraído
    next_action: str