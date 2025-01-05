from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models.user import User
from google.oauth2 import id_token
from google.auth.transport import requests

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

        user = User(username=username, password=password)
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

        user = User(username=username)
        user.password_hash = user_data.get("password_hash", "")

        if not user.check_password(password):
            return jsonify({"error": "Invalid username or password"}), 401

        access_token = create_access_token(identity={"user_id": user_data["user_id"], "username": username})
        return jsonify({"message": "Login successful", "access_token": access_token}), 200

    @auth_bp.route('/google-login', methods=['POST'])
    def google_login():
        data = request.json
        token = data.get("id_token")
        if not token:
            return jsonify({"error": "Google ID token is required"}), 400

        try:
            # Verify the token with Google
            CLIENT_ID = "690904482528-n6eh7jf42cbui0l33m0l7gjjn5j9vn90.apps.googleusercontent.com"  # Replace with your actual Google Client ID
            id_info = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

            email = id_info.get("email")
            google_id = id_info.get("sub")
            username = id_info.get("name")

            if not email or not google_id:
                return jsonify({"error": "Invalid Google token"}), 400

            # Check if the user already exists in the database
            user_data = db.users.find_one({"google_id": google_id})
            if not user_data:
                # Create a new user for first-time login
                user = User(username=username, google_id=google_id, email=email)
                db.users.insert_one(user.to_dict())
                user_data = user.to_dict()

            access_token = create_access_token(identity={"user_id": user_data["user_id"], "username": username})
            return jsonify({"message": "Login successful", "access_token": access_token}), 200

        except ValueError:
            return jsonify({"error": "Invalid Google ID token"}), 401

    return auth_bp
