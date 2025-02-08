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
                print("Database 'target_db' created successfully.")

            # Close connection to the default Postgres database
            cursor.close()
            conn.close()
            return True

        except Error as error:
            print(f"Error during database initialization: {error}.")
            return False
        
    @staticmethod
    def table_exists(table_name):
        """Checks whether a table already exists in the database."""
        try:
            # Connect to the target database
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Check if the table exists in the current schema
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = %s
                )
            """, (table_name))

            exists = cursor.fetchone()[0]

            # Close connection to the target database
            cursor.close()
            conn.close()
            return exists
        
        except Error as error:
            print(f"Error checking table existence: {error}.")
            return False

    @staticmethod
    def create_table(table_name, columns):
        """Creates a table only if it doesn't exist."""
        # First check if the table already exists
        if DatabaseManager.table_exists(table_name):
            print(f"Table '{table_name}' already exists. Skipping creation and data insertion.")
            return False
        
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

            # Create the column definitions
            column_definitions = []
            for col_name, col_type in columns.items():
                pg_type = type_mapping.get(col_type.split('(')[0], 'TEXT')
                column_definitions.append(f"{col_name} {pg_type}")

            # Create the table
            column_definitions = ", ".join(column_definitions)
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})")

            # Close connection to the target database
            cursor.close()
            conn.close()
            return True

        except Error as error:
            print(f"Error creating table: {error}.")
            return False
    
    @staticmethod
    def insert_data(table_name, column_names, records):
        """Inserts data only if the table was just created."""
        # If the table existed before, skip insertion
        if DatabaseManager.table_exists(table_name):
            return False

        try:
            # Connect to the target database
            conn = psycopg2.connect(**DB_CONFIG)
            conn.set_session(autocommit=True)
            cursor = conn.cursor()

            # Prepare the insert statement
            placeholders = ", ".join(["%s"] * len(column_names))
            col_names = ", ".join(column_names)
            insert_query = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"

            # Insert all records
            for record in records:
                values = tuple(record.get(col) for col in column_names)
                cursor.execute(insert_query, values)

            # Close connection to the target database
            cursor.close()
            conn.close()
            return True

        except Error as error:
            print(f"Error inserting data: {error}.")
            return False
