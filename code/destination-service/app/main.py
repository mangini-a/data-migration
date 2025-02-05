from app.routes import app

def run_server(host='localhost', port=5000):
    app.run(host=host, port=port)

if __name__ == "__main__":
    run_server()
