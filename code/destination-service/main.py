import psycopg2
from psycopg2 import Error

try:
    # First connect to default 'postgres' database to create our new database
    conn = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="the_doors_of_perception",
        host="127.0.0.1",
        port="5432"
    )

    # Make sure that every statement sent to the backend has immediate effect
    conn.set_session(autocommit=True)
    
    # Create a cursor to perform database operations
    cursor = conn.cursor()

    # Check if database exists first to avoid errors
    cursor.execute("SELECT 1 FROM pg_database WHERE datname='postgres_db'")
    exists = cursor.fetchone()

    if not exists:
        cursor.execute("CREATE DATABASE postgres_db")
        print("Database 'postgres_db' created succesfully")
    
    # Close connection to 'postgres' database
    cursor.close()
    conn.close()

    # Now connect to our new database
    conn = psycopg2.connect(
        database="postgres_db",
        user="postgres",
        password="the_doors_of_perception",
        host="127.0.0.1",
        port="5432"
    )

    conn.set_session(autocommit=True)
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            price DECIMAL(10, 2)
        )
    """)
    print("Table 'products' is ready")

    # Test insertion
    cursor.execute("""
        INSERT INTO products (name, price)
        VALUES (%s, %s)
        """, 
        ("Test Product", 19.99)
    )
    print("Test record inserted succesfully")

except Error as error:
    print(f"Error while operating on PostgreSQL: {error}")

finally:
    if 'conn' in locals():
        cursor.close()
        conn.close()
        print("PostgreSQL connection is closed")
