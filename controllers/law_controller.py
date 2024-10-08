from flask import Blueprint, jsonify, request

# הגדרת קונטרולר בשם 'user'
law_bp = Blueprint('law_bp', __name__)

@law_bp.route('/laws', methods=['GET'])
def get_users():
    users = ["Alice", "Bob", "Charlie"]
    return jsonify({"users": users})

@law_bp.route('/laws', methods=['POST'])
def create_user():
    user_data = request.json
    return jsonify({"message": "User created", "user": user_data}), 201
