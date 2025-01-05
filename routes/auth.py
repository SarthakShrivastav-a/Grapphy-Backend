from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models.user import User

auth_bp = Blueprint('auth', __name__)

def init_auth_routes(db):
    @auth_bp.route('/register', methods=['POST'])
    def register():
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        if db.users.find_one({"username": username}):
            return jsonify({"error": "Username already exists"}), 400

        user = User(username, password)
        db.users.insert_one(user.to_dict())
        return jsonify({"message": "User registered successfully"}), 201

    @auth_bp.route('/login', methods=['POST'])
    def login():
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        user_data = db.users.find_one({"username": username})
        if not user_data:
            return jsonify({"error": "Invalid username or password"}), 401

        user = User(username)
        user.password_hash = user_data["password_hash"]
        
        if not user.check_password(password):
            return jsonify({"error": "Invalid username or password"}), 401

        access_token = create_access_token(identity={"user_id": user_data["user_id"], "username": username})
        return jsonify({"message": "Login successful", "access_token": access_token}), 200

    return auth_bp