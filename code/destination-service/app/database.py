import psycopg2
from psycopg2 import Error
from app.config import DB_CONFIG

class DatabaseManager:
    @staticmethod
    def init_database():
        try:
            # Connect to the default Postgres database
            conn = psycopg2.connect(
                database="postgres",
                **{k: v for k, v in DB_CONFIG.items() if k != 'database'}
            )

            # Make sure that every statement sent to the backend has immediate effect
            conn.set_session(autocommit=True)

            # Create a cursor to be able to execute database operations
            cursor = conn.cursor()

            # Check whether the target database already exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname='target_db'")
            exists = cursor.fetchone()

            # If not, create the target database
            if not exists:
                cursor.execute("CREATE DATABASE target_db")
                print("Database 'target_db' created successfully")

            # Close the connection to the default Postgres database
            cursor.close()
            conn.close()

        except Error as error:
            print(f"Error during database initialization: {error}")

    @staticmethod
    def create_table(table_name, columns, column_types):
        try:
            # Connect to the target database
            conn = psycopg2.connect(**DB_CONFIG)
            conn.set_session(autocommit=True)
            cursor = conn.cursor()

            # Map MySQL data types to PostgreSQL data types
            type_mapping = {
                'int': 'INTEGER',
                'text': 'TEXT',
                'varchar': 'VARCHAR',
                'date': 'DATE',
                'enum': 'TEXT',
                'datetime': 'TIMESTAMP',
                'timestamp': 'TIMESTAMP',
                'bigint': 'BIGINT',
                'float': 'REAL',
                'double': 'DOUBLE PRECISION',
                'decimal': 'NUMERIC',
                'boolean': 'BOOLEAN'
            }

            # Associate each column in the table with the correct Postgres data type
            column_definitions = []
            for col, col_type in column_types.items():
                pg_type = type_mapping.get(col_type.split('(')[0], 'TEXT')
                column_definitions.append(f"{col} {pg_type}")

            # Perform a query to create the table
            column_definitions = ", ".join(column_definitions)
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})")

            # Close the connection to the target database
            cursor.close()
            conn.close()

        except Error as error:
            print(f"Error creating table: {error}")
    
    @staticmethod
    def insert_data(table_name, columns, data):
        try:
            # Connect to the target database
            conn = psycopg2.connect(**DB_CONFIG)
            conn.set_session(autocommit=True)
            cursor = conn.cursor()

            # Prepare the statement to be executed
            placeholders = ", ".join(["%s"] * len(columns))
            column_names = ", ".join(columns)
            insert_query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

            # Perform a query to insert data for each table record
            for record in data:
                values = tuple(record.get(col) for col in columns)
                cursor.execute(insert_query, values)

            # Close the connection to the target database
            cursor.close()
            conn.close()

        except Error as error:
            print(f"Error inserting data: {error}")
