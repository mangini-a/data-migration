import psycopg2
from psycopg2 import Error

try:
    # Connect to an existing database
    conn = psycopg2.connect(
        database="postgres_db",
        user="postgres",
        password="the_doors_of_perception",
        host="127.0.0.1",
        port="5432"
    )

    # Make sure that every statement sent to the backend has immediate effect
    conn.set_session(autocommit=True)
    
    # Create a cursor to perform database operations
    cursor = conn.cursor()

    # Execute a SQL query
    cursor.execute("DROP TABLE products")
    # cursor.execute("CREATE DATABASE postgres_db")

    # Fetch the result
    # record = cursor.fetchone()
    # print("You are connected to - ", record, "\n")

except Error as error:
    print("Error while operating on the PostgreSQL database: ", error)

finally:
    if conn:
        cursor.close()
        conn.close()
        print("PostgreSQL connection is closed")
