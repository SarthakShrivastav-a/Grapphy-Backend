from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
import google.generativeai as genai

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/chatDatabase"
db = PyMongo(app).db

genai.configure(api_key="AIzaSyDKvJBGxmhAYjC7O5stDTBHeexdLT6VlMo")
model = genai.GenerativeModel(model_name='gemini-1.5-flash')

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    chat_id = data.get("chat_id")
    user_id = data.get("user_id")
    user_message_text = data.get("text")
    topic = data.get("topic", "New Chat")

    if not user_message_text or not user_id:
        return jsonify({"error": "User ID and message text are required"}), 400

    user_message = {
        "message_id": str(ObjectId()),
        "role": "user",
        "timestamp": data.get('timestamp'),
        "type": "text",
        "content": {"text": user_message_text}
    }

    chat = db.chats.find_one({"chat_id": chat_id})
    if not chat:
        chat_id = str(ObjectId())
        chat = {
            "chat_id": chat_id,
            "user_id": user_id,
            "created_at": data.get('timestamp'),
            "updated_at": data.get('timestamp'),
            "topic": topic,
            "messages": [user_message]
        }
        db.chats.insert_one(chat)
    else:
        db.chats.update_one(
            {"chat_id": chat_id},
            {"$push": {"messages": user_message}, "$set": {"updated_at": data.get('timestamp'),}}
        )

    try:
        ai_response = model.generate_content(user_message_text)
        ai_message_text = ai_response.text
    except Exception as e:
        ai_message_text = f"Error generating AI response: {str(e)}"

    ai_message = {
        "message_id": str(ObjectId()),
        "role": "assistant",
        "timestamp": data.get('timestamp'),
        "type": "text",
        "content": {"text": ai_message_text}
    }

    db.chats.update_one(
        {"chat_id": chat_id},
        {"$push": {"messages": ai_message}, "$set": {"updated_at": datetime.utcnow().isoformat()}}
    )

    return jsonify({"chat_id": chat_id, "user_message": user_message, "ai_message": ai_message}), 200

@app.route('/create_chat', methods=['POST'])
def create_chat():
    data = request.json
    user_id = data.get("user_id")
    topic = data.get("topic", "New Chat")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    # Validate user_id exists in the database
    user = db.users.find_one({"user_id": user_id})
    if not user:
        return jsonify({"error": "Invalid user ID"}), 401

    chat_id = str(ObjectId())
    chat = {
        "chat_id": chat_id,
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "topic": topic,
        "messages": []
    }
    db.chats.insert_one(chat)

    return jsonify({"chat_id": chat_id}), 201


@app.route('/get_chats', methods=['GET'])
def get_chats():
    user_id = request.headers.get("user_id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    chats = list(db.chats.find({"user_id": user_id}, {"_id": 0, "chat_id": 1, "topic": 1, "updated_at": 1}))
    return jsonify({"chats": chats}), 200


@app.route('/get_chat/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    chat = db.chats.find_one({"chat_id": chat_id}, {"_id": 0})
    if chat:
        return jsonify(chat), 200
    return jsonify({"error": "Chat not found"}), 404



#registration
import bcrypt

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Check if the username already exists
    if db.users.find_one({"username": username}):
        return jsonify({"error": "Username already exists"}), 400

    # Hash the password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Create the user
    user = {
        "user_id": str(ObjectId()),
        "username": username,
        "password_hash": password_hash.decode('utf-8'),
        "created_at": data.get('timestamp'),
    }
    db.users.insert_one(user)

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Find the user
    user = db.users.find_one({"username": username})
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    # Verify the password
    if not bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
        return jsonify({"error": "Invalid  password"}), 401

    return jsonify({"message": "Login successful", "user_id": user["user_id"]}), 200







if __name__ == "__main__":
    app.run(debug=True)
