from flask import Flask, request, jsonify
from app.database import DatabaseManager

app = Flask(__name__)

@app.route('/receive', methods=['POST'])
def receive_data():
    try:
        # Parse incoming JSON data
        data = request.get_json()

        # Validate required fields
        table_name = data.get('table')
        columns = data.get('columns')
        records = data.get('data')

        if not table_name or not columns or not records:
            return jsonify({
                "status": "error", 
                "message": "Invalid data format or missing required fields."
            }), 400
        
        # If table exists, return early without doing anything
        if DatabaseManager.table_exists(table_name):
            return jsonify({
                "status": "success",
                "message": f"Table '{table_name}' has already been migrated. No actions taken."
            }), 200

        # Create table and insert data only if the table didn't exist
        if DatabaseManager.create_table(table_name, columns):
            if DatabaseManager.insert_data(table_name, list(columns.keys()), records):
                return jsonify({
                    "status": "success", 
                    "message": f"Created table '{table_name}' and inserted data successfully."
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": f"Created table '{table_name}' but failed to insert data."
                }), 500
        else:
            return jsonify({
                "status": "error",
                "message": f"Failed to create table '{table_name}'."
            }), 500
    
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Server error: {str(e)}."
        }), 500
