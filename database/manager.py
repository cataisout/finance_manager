import psycopg2
from psycopg2 import sql
from datetime import datetime
from zoneinfo import ZoneInfo


class DatabaseManager:

    def __init__(self, connection_uri: str) -> None:
        self.conn = psycopg2.connect(connection_uri)


    def create_tables(self) -> None:
        query = """
        CREATE TABLE spend_registry (
            id SERIAL PRIMARY KEY,
            value NUMERIC(10, 2) NOT NULL,
            description VARCHAR(500) NOT NULL,
            category VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS monthly_budget (
        id SERIAL PRIMARY KEY,
        category VARCHAR(50) NOT NULL,
        amount NUMERIC(10, 2) NOT NULL,
        month INT NOT NULL,
        year INT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (category, month, year)
        );
            """

        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e


    def insert_spend(self, value: float, description: str,  category: str, created_at: datetime | None = None) -> None:

        query = """
        INSERT INTO spend_registry (value, description, category, created_at)
        VALUES (%s, %s, %s, %s);
        """

        created_at = created_at or datetime.now(ZoneInfo("America/Sao_Paulo"))

        with self.conn.cursor() as cur:
            cur.execute(query, (value, description, category, created_at))

        self.conn.commit()

    def set_monthly_budget(self, category: str, amount: float):
        query = """
        INSERT INTO monthly_budget (category, amount, month, year)
        VALUES (%s, %s, EXTRACT(MONTH FROM CURRENT_DATE), EXTRACT(YEAR FROM CURRENT_DATE))
        ON CONFLICT (category, month, year)
        DO UPDATE SET amount = EXCLUDED.amount;
        """

        with self.conn.cursor() as cur:
            cur.execute(query, (category, amount))

        self.conn.commit()
    
    def get_current_month_total_by_category(self, category: str):
        query = """
        SELECT COALESCE(SUM(value), 0)
        FROM spend_registry
        WHERE category = %s
        AND EXTRACT(MONTH FROM created_at) = EXTRACT(MONTH FROM CURRENT_DATE)
        AND EXTRACT(YEAR FROM created_at) = EXTRACT(YEAR FROM CURRENT_DATE);
        """

        with self.conn.cursor() as cur:
            cur.execute(query, (category,))
            return cur.fetchone()[0]
    
    def get_remaining_budget(self, category: str):
        query = """
        SELECT amount
        FROM monthly_budget
        WHERE category = %s
        AND month = EXTRACT(MONTH FROM CURRENT_DATE)
        AND year = EXTRACT(YEAR FROM CURRENT_DATE);
        """

        with self.conn.cursor() as cur:
            cur.execute(query, (category,))
            result = cur.fetchone()

        if not result:
            return None

        budget = result[0]
        spent = self.get_current_month_total_by_category(category)

        return float(budget) - float(spent)
        

    def get_all_spends(self):
        query = "SELECT * FROM spend_registry;"

        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
                results = cur.fetchall()
            return results
        except Exception as e:
            raise e
        

    def close(self):
        if self.conn:
            self.conn.close()



