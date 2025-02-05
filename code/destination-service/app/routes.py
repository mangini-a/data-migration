from flask import Flask, request, jsonify
from app.database import DatabaseManager

app = Flask(__name__)

@app.route('/receive', methods=['POST'])
def receive_data():
    try:
        # Parse data coming from the servlet as JSON
        data = request.get_json()

        # Get what is required to create and populate the table
        table_name = data.get('table')
        columns = data.get('columns')
        column_types = data.get('columnTypes')
        records = data.get('data')

        if not table_name or not columns or not column_types or not records:
            return jsonify({"status": "error", "message": "Invalid data format"}), 400
        
        DatabaseManager.create_table(table_name, columns, column_types)
        DatabaseManager.insert_data(table_name, columns, records)

        return jsonify({"status": "success", "message": f"Data inserted into {table_name}"}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500
