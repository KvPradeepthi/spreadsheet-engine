import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from parser import FormulaParser
from graph_manager import GraphManager
from evaluator import Evaluator

app = Flask(__name__)
CORS(app)

API_PORT = int(os.getenv('API_PORT', 8080))

# In-memory sheet storage
sheets = {}
parser = FormulaParser()
graph_manager = GraphManager()
evaluator = Evaluator(parser, graph_manager)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/sheets/<sheet_id>/cells/<cell_id>', methods=['PUT'])
def set_cell(sheet_id, cell_id):
    try:
        data = request.get_json()
        value = data.get('value')
        
        if sheet_id not in sheets:
            sheets[sheet_id] = {}
        
        sheets[sheet_id][cell_id] = value
        graph_manager.update_dependencies(sheet_id, cell_id, value, sheets)
        evaluator.recalculate(sheet_id, sheets, graph_manager)
        
        return jsonify({}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/sheets/<sheet_id>/cells/<cell_id>', methods=['GET'])
def get_cell(sheet_id, cell_id):
    if sheet_id not in sheets or cell_id not in sheets[sheet_id]:
        return jsonify({}), 404
    
    value = sheets[sheet_id][cell_id]
    return jsonify({"value": value}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=API_PORT, debug=False)
