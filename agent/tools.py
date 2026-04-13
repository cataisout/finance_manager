from langchain.tools import tool
from datetime import datetime


@tool("add_spend_new_registry")
def add_registry(value: float, description: str, created_at: datetime, category: str, db_manager):
    """registra um gasto novo no banco"""
    try:
        db_manager.insert_spend(value=value, description=description, created_at=created_at, category=category)
    except Exception as e :
        print(f"[add_registry - Exception] {e}")
