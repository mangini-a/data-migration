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
            
            # Create a cursor to perform database operations
            cursor = conn.cursor()

            # Check if the target database already exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname='target_db'")
            exists = cursor.fetchone()

            # If not, create it
            if not exists:
                cursor.execute("CREATE DATABASE target_db")
                print("Target database created succesfully")
            
            # Close the connection to the default Postgres database
            cursor.close()
            conn.close()

            # Now connect to the target database
            conn = psycopg2.connect(**DB_CONFIG)
            conn.set_session(autocommit=True)
            cursor = conn.cursor()

            # Create the received table locally
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    price DECIMAL(10, 2)
                )
            """)
            print("Table initialized succesfully")

            # Close the connection to the target database
            cursor.close()
            conn.close()
            return True

        except Error as error:
            print(f"Error during database initialization: {error}")
            return False
        
    @staticmethod
    def create_table_if_not_exists(table_name, columns):
        try:
            # Connect to the target database
            conn = psycopg2.connect(**DB_CONFIG)
            conn.set_session(autocommit=True)
            cursor = conn.cursor()

            column_definitions = ", ".join([f"{col} TEXT" for col in columns])
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

            placeholders = ", ".join(["%s"] * len(columns))
            column_names = ", ".join(columns)
            insert_query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
            for record in data:
                values = tuple(record.get(col) for col in columns)
                cursor.execute(insert_query, values)

            # Close the connection to the target database
            cursor.close()
            conn.close()

        except Error as error:
            print(f"Error inserting data: {error}")
    
    @staticmethod
    def process_data(data):
        """
        Processes the received JSON-formatted string and stores it in the database.\n
        Returns a tuple of (success_boolean, message_string, records_processed_count)
        """
        try:
            # Connect to the target database
            conn = psycopg2.connect(**DB_CONFIG)
            conn.set_session(autocommit=True)
            cursor = conn.cursor()

            records_processed = 0
            # Process each record in the received data (...)
            for record in data.get('records', []):
                cursor.execute(
                    "INSERT INTO products (name, price) VALUES (%s, %s)",
                    (record.get('name'), record.get('price'))
                )
                records_processed += 1

            # Close the connection to the target database and return the tuple
            cursor.close()
            conn.close()
            return True, f"Successfully processed {records_processed} records", records_processed
        
        except Error as error:
            return False, f"Database error: {str(error)}", 0
        
        except Exception as e:
            return False, f"Processing error: {str(e)}", 0
