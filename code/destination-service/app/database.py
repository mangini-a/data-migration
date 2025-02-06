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
            return True

        except Error as error:
            print(f"Error during database initialization: {error}")
            return False

    @staticmethod
    def create_table(table_name, columns):
        try:
            # Connect to the target database
            conn = psycopg2.connect(**DB_CONFIG)
            conn.set_session(autocommit=True)
            cursor = conn.cursor()

            # Map MySQL data types in use to Postgres data types
            type_mapping = {
                'date': 'DATE',
                'enum': 'TEXT',
                'int': 'INTEGER',
                'text': 'TEXT',
                'varchar': 'VARCHAR'
            }

            # Associate each column in the table with the correct Postgres data type
            column_definitions = []
            for col_name, col_type in columns.items():
                pg_type = type_mapping.get(col_type.split('(')[0], 'TEXT')
                column_definitions.append(f"{col_name} {pg_type}")

            # Perform a query to create the table
            column_definitions = ", ".join(column_definitions)
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})")

            # Close the connection to the target database
            cursor.close()
            conn.close()

        except Error as error:
            print(f"Error creating table: {error}")
    
    @staticmethod
    def insert_data(table_name, column_names, records):
        try:
            # Connect to the target database
            conn = psycopg2.connect(**DB_CONFIG)
            conn.set_session(autocommit=True)
            cursor = conn.cursor()

            # Prepare the statement to be executed
            placeholders = ", ".join(["%s"] * len(column_names))
            col_names = ", ".join(column_names)
            insert_query = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"

            # Perform a query to insert data for each table record
            for record in records:
                values = tuple(record.get(col) for col in column_names)
                cursor.execute(insert_query, values)

            # Close the connection to the target database
            cursor.close()
            conn.close()

        except Error as error:
            print(f"Error inserting data: {error}")
