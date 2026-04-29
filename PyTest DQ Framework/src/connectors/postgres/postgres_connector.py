import psycopg2
import pandas as pd


class PostgresConnectorContextManager:
    """Context manager for PostgreSQL database connections."""

    def __init__(self, db_host: str, db_name: str, db_user: str, db_password: str, db_port: int = 5432):
        """
        Initialize PostgreSQL connection parameters.

        Args:
            db_host: PostgreSQL server host
            db_name: Database name
            db_user: Database user
            db_password: Database password
            db_port: PostgreSQL server port (default: 5432)
        """
        self.db_host = db_host
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_port = db_port
        self.connection = None

    def __enter__(self):
        """Establish database connection."""
        try:
            self.connection = psycopg2.connect(
                host=self.db_host,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                port=self.db_port
            )
            return self
        except psycopg2.Error as e:
            raise ConnectionError(f"Failed to connect to PostgreSQL: {str(e)}")

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Close database connection."""
        if self.connection:
            self.connection.close()
        return False

    def get_data_sql(self, sql: str) -> pd.DataFrame:
        """
        Execute SQL query and return result as pandas DataFrame.

        Args:
            sql: SQL query string

        Returns:
            pandas DataFrame with query results

        Raises:
            ValueError: If connection is not established
            psycopg2.Error: If SQL execution fails
        """
        if not self.connection:
            raise ValueError("Database connection is not established")

        try:
            return pd.read_sql_query(sql, self.connection)
        except psycopg2.Error as e:
            raise RuntimeError(f"Failed to execute SQL query: {str(e)}")

