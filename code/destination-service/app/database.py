import psycopg2
from psycopg2 import Error
from app.config import DB_CONFIG

class DatabaseManager:
    @staticmethod
    def init_database():
        """
        Creates the target database if it does not already exist.

        Returns:
            bool: True if it exists or is created successfully, False if an error occurs
        """
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
        
        finally:
            # Ensure connections are closed even if an error occurs
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()
        
    @staticmethod
    def table_exists(table_name):
        """
        Checks if a table exists in the database using PostgreSQL's native system catalog.

        Args:
            table_name (str): Name of the table to check

        Returns:
            bool: True if the table exists, False otherwise
        """
        try:
            # Connect to the target database with autocommit enabled
            conn = psycopg2.connect(**DB_CONFIG)
            conn.set_session(autocommit=True)
            cursor = conn.cursor()

            # Query PostgreSQL's system catalog
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1
                    FROM pg_tables
                    WHERE tablename = %s
                    AND schemaname = 'public'
                )
            """, (table_name,))

            # Get the boolean result
            exists = cursor.fetchone()[0]

            # Close connection to the target database
            cursor.close()
            conn.close()

            return exists
        
        except Error as error:
            print(f"Error checking table existence: {error}.")
            return False
        
        finally:
            # Ensure connections are closed even if an error occurs
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()

    @staticmethod
    def create_table(table_name, columns):
        """
        Creates a table from the specified schema.

        Args:
            table_name (str): Name of the new table
            columns: Object mapping each column to the corresponding data type

        Returns:
            bool: True if it is created successfully, False if an error occurs
        """
        try:
            # Connect to the target database with autocommit enabled
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
            cursor.execute(f"CREATE TABLE {table_name} ({column_definitions})")

            # Close connection to the target database
            cursor.close()
            conn.close()
            return True

        except Error as error:
            print(f"Error creating table: {error}.")
            return False
        
        finally:
            # Ensure connections are closed even if an error occurs
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()
    
    @staticmethod
    def insert_data(table_name, column_names, records):
        """
        Inserts records into the specified table using Postgres data types.

        Args:
            table_name (str): Name of the target table
            column_names (list): List of the target table's columns
            records: Object containing the entries to be inserted

        Returns:
            bool: True if data is entered successfully, False if an error occurs
        """
        try:
            # Connect to the target database with autocommit enabled
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
        
        finally:
            # Ensure connections are closed even if an error occurs
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()
