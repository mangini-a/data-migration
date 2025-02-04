from flask import Flask, request, jsonify
from app.database import DatabaseManager

app = Flask(__name__)

@app.route('/receive', methods=['POST'])
def receive_data():
    try:
        data = request.get_json()
        success, message, records_processed = DatabaseManager.process_data(data)
        if success:
            return jsonify({"status": "success", "message": message}), 200
        else:
            return jsonify({"status": "error", "message": message}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500
