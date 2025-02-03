from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import psycopg2
from psycopg2 import Error

# Target database configuration used throughout the application
DB_CONFIG = {
    "database": "postgres_db",
    "user": "postgres",
    "password": "the_doors_of_perception",
    "host": "127.0.0.1",
    "port": "5432"
}

class DatabaseManager:
    """Handles all database operations, including initialization and data processing."""
    @staticmethod
    def init_database():
        """
        Initializes the database and creates the necessary tables if they don't exist.\n
        Returns True if successful, False if an error occurs.
        """
        try:
            # Connect to the default database to create the target database (if necessary)
            conn = psycopg2.connect(
                database="postgres",
                **{k: v for k, v in DB_CONFIG.items() if k != 'database'}
            )

            # Make sure that every statement sent to the backend has immediate effect
            conn.set_session(autocommit=True)
            
            # Create a cursor to perform database operations
            cursor = conn.cursor()

            # Check if the target database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname='postgres_db'")
            exists = cursor.fetchone()

            if not exists:
                cursor.execute("CREATE DATABASE postgres_db")
                print("Database 'postgres_db' created succesfully")
            
            # Close the connection to the default database
            cursor.close()
            conn.close()

            # Now connect to the target database to create tables
            conn = psycopg2.connect(**DB_CONFIG)
            conn.set_session(autocommit=True)
            cursor = conn.cursor()

            # Create tables (...)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    price DECIMAL(10, 2)
                )
            """)
            print("Tables initialized succesfully")

            # Close the connection to the target database
            cursor.close()
            conn.close()
            return True

        except Error as error:
            print(f"Error during database initialization: {error}")
            return False
        
    @staticmethod
    def process_data(data):
        """
        Processes the received JSON data and stores it in the database.\n
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
                    """
                    INSERT INTO products (name, price)
                    VALUES (%s, %s)
                    """,
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
        
class MigrationRequestHandler(BaseHTTPRequestHandler):
    """
    Handles incoming HTTP requests from the Jakarta servlet.\n
    This class defines how the server responds to different types of requests.
    """
    def _send_response(self, status_code, message):
        """Helper method to send JSON responses."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = json.dumps({
            "status": "success" if status_code == 200 else "error",
            "message": message
        })
        self.wfile.write(response.encode("utf-8"))

    def do_POST(self):
        """Handles POST requests from the Jakarta servlet."""
        if self.path == '/receive':
            # Read and parse the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                # Deserialize the request body to a Python object
                data = json.loads(post_data.decode("utf-8"))
                success, message, records_processed = DatabaseManager.process_data(data)

                if success:
                    self._send_response(200, message)
                else:
                    self._send_response(500, message)

            except json.JSONDecodeError:
                self._send_response(400, "Invalid JSON data received")
            except Exception as e:
                self._send_response(500, f"Server error: {str(e)}")

        else:
            self._send_response(404, "Endpoint not found")

    def run_server(host='localhost', port=5000):
        """
        Initializes the local database and starts the HTTP server.
        This is the main entry point for the application.
        """
        # Initialize the local database before starting the server
        if not DatabaseManager.init_database():
            print("Failed to initialize database. Server will not start.")
            return
        
        # Create and listen at the HTTP socket, dispatching the requests to a handler
        server_address = (host, port)
        httpd = HTTPServer(server_address, MigrationRequestHandler)
        print(f"Server running on http://{host}:{port}")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()

    if __name__ == "__main__":
        run_server()
