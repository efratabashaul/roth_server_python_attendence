from flask import Blueprint, jsonify, request
import requests

# הגדרת קונטרולר בשם 'user'
user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    users = ["Alice", "Bob", "Charlie"]
    return jsonify({"users": users})

#CHECKINGGG
@user_bp.route('/check-nest', methods=['POST'])
def check_connect_nest():
    response = requests.post('http://localhost:3000/users', json={"tasks": "example task"})

    try:
        # convert the response content to json or text
        response_data = response.json()  # convert to json if response is json
    except ValueError:
        response_data = response.text  # fallback to text if not a valid json

    return jsonify({"message": "connect to nest successfully", "summary": response_data}), 200
