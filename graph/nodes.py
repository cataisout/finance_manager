from graph.state import State
from langchain_core.messages import AIMessage

schema = {
    "type": "object",
    "properties": {
        "intent": {
            "type": "string",
            "enum": [
                "register_expense",
                "get_expenses",
                "set_budget",
                "get_remaining_budget",
                "unknown"
            ]
        },
        "value": {"type": "number"},
        "description": {"type": "string"},
        "category": {
            "type": "string",
            "enum": [
                    "alimentação",
                    "transporte",
                    "moradia",
                    "entretenimento",
                    "saúde",
                    "educação",
                    "outros",
                    "investimentos"
                ]
        }
    },
    "required": ["intent"]
}


def detect_intent_node(state: State, agent):

    user_input = state["messages"][-1].content

    result = agent.structured_invoke(
        user_input=user_input,
        schema=schema
    )
    print(result)

    return {
        "intent": result.get("intent", "unknown"),
        "data": result,
        "next_action": result.get("intent", "unknown")
    }


def execute_ad_registry_node(state: State, db_manager):

    print(f"execute_ad_registry_node - Recieved state {state}")

    if not state["data"].get("description"):
        description = state["data"]["category"]
    try:
        db_manager.insert_spend(
            value=state["data"]["value"],
            description=description,
            category=state["data"]["category"],
        )
        return {"messages": [AIMessage(content="Gasto registrado com sucesso! ✅")]}

    except Exception as e:
        print(f"[execute_ad_registry_node - Exception] {e}")
        return {"messages": [AIMessage(content=f"Não foi possível registrar o gasto. Erro: {e}")]}


def execute_set_budget_node(state: State, db_manager):

    print(f"execute_set_budget_node - Recieved state {state}")
    try:

        category = state['data']['category']
        value = state['data']['value']
        db_manager.set_monthly_budget(category, value)
        return {"messages": [AIMessage(content="Orçamento registrado com sucesso! ✅")]}

    except Exception as e:
        print(f"[execute_ad_registry_node - Exception] {e}")
        return {"messages": [AIMessage(content=f"Não foi possível registrar o orçamento. Erro: {e}")]}


def execute_get_remaining_budget(state: State, db_manager):

    print(f"execute_get_remaining_budget - Recieved state {state}")
    try:

        category = state['data']['category']
        remaining = db_manager.get_remaining_budget(category)
        return {"messages": [AIMessage(content=f"Apenas R$ {remaining}  restantes em {category}")]}

    except Exception as e:
        print(f"[execute_ad_registry_node - Exception] {e}")
        return {"messages": [AIMessage(content=f"Não foi possível buscar o orçamento. Erro: {e}")]}



def current_month_total_by_category_node(state: State, db_manager):

    print(f"current_month_total_by_category_node - Recieved state {state}")
    try:
        category = state['data']['category']
        spend = db_manager.get_current_month_total_by_category(category)
        return {"messages": [AIMessage(content=f"Neste mês, você gastou R$ {spend} em {category}")]}

    except Exception as e:
        print(f"[execute_ad_registry_node - Exception] {e}")
        return {"messages": [AIMessage(content=f"Não foi possível fazer essa consulta. Erro: {e}")]}

