from flask import Blueprint, jsonify, request
from services.summarize_service import main
import asyncio

summarize_bp = Blueprint('summarize_bp', __name__)


@summarize_bp.route('/summarize', methods=['POST'])
def create_task():
    task_data = request.json.get("text")
    result = main(task_data)
    if result == "NO_VALID_TASKS_FOUND":
        return jsonify({"message": "No valid tasks found. Please try again with relevant tasks."}), 400
    return jsonify({"message": "Task summarized successfully", "summary": result}), 200


