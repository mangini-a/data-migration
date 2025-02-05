from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/receive', methods=['POST'])
def receive_data():
    try:
        data = request.get_json()

        table_name = data.get('table')
        print(f"Received table: {table_name}")

        columns = data.get('columns')
        print(f"{table_name}'s columns: {columns}")

        records = data.get('data')

        if not table_name or not columns or not records:
            return jsonify({"status": "error", "message": "Invalid data format"}), 400

        return jsonify({"status": "success", "message": "Data received successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500
