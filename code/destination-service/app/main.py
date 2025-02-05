from app.database import DatabaseManager
from app.routes import app

def run_server(host='localhost', port=5000):
    if not DatabaseManager.init_database():
        print("Failed to initialize database. Server will not start.")
        return
    app.run(host=host, port=port)

if __name__ == "__main__":
    run_server()
