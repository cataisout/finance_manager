from functools import partial
from langgraph.graph import StateGraph, START, END
from graph.nodes import *
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


def router_after_intent(state: State):
    intent = state.get("next_action")

    if intent == "register_expense":
        return "execute_add_registry_node"
    
    elif intent == "get_expenses":
        return "current_month_total_by_category_node"
    
    elif intent == "set_budget":
        return "execute_set_budget_node"
    
    elif intent == "get_remaining_budget":
        return "execute_get_remaining_budget"
    
    else:  # unknown
        return END
    
    
def build_graph(agent, db_manager):

    graph = StateGraph(State)
    graph.add_node("detect_intent", partial(detect_intent_node, agent=agent))
    graph.add_node("execute_add_registry_node", partial(execute_ad_registry_node, db_manager=db_manager))
    graph.add_node("execute_set_budget_node", partial(execute_set_budget_node, db_manager=db_manager))
    graph.add_node("execute_get_remaining_budget", partial(execute_get_remaining_budget, db_manager=db_manager))
    graph.add_node("current_month_total_by_category_node", partial(current_month_total_by_category_node, db_manager=db_manager))
    

    # Flow
    graph.add_edge(START, "detect_intent")
    graph.add_conditional_edges("detect_intent", router_after_intent)

    # End connections
    graph.add_edge("execute_add_registry_node", END)
    graph.add_edge("execute_set_budget_node", END)
    graph.add_edge("execute_get_remaining_budget", END)
    graph.add_edge("current_month_total_by_category_node", END)

    return graph.compile()
    
