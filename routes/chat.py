from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.chat import Chat

chat_bp = Blueprint('chat', __name__)

def init_chat_routes(db, message_service):
    @chat_bp.route('/get_chats', methods=['GET'])
    @jwt_required()
    def get_chats():
        current_user = get_jwt_identity()
        user_id = current_user["user_id"]

        chats = list(db.chats.find(
            {"user_id": user_id},
            {"_id": 0, "chat_id": 1, "topic": 1, "updated_at": 1}
        ))
        return jsonify({"chats": chats}), 200

    @chat_bp.route('/create_chat', methods=['POST'])
    @jwt_required()
    def create_chat():
        current_user = get_jwt_identity()
        user_id = current_user["user_id"]
        data = request.json
        topic = data.get("topic", "New Chat")

        chat = Chat(user_id, topic)
        db.chats.insert_one(chat.to_dict())
        return jsonify({"chat_id": chat.chat_id}), 201

    @chat_bp.route('/get_chat/<chat_id>', methods=['GET'])
    @jwt_required()
    def get_chat(chat_id):
        current_user = get_jwt_identity()
        user_id = current_user["user_id"]

        chat = db.chats.find_one({"chat_id": chat_id, "user_id": user_id}, {"_id": 0})
        if chat:
            return jsonify(chat), 200
        return jsonify({"error": "Chat not found"}), 404

    @chat_bp.route('/send_message', methods=['POST'])
    @jwt_required()
    def send_message():
        current_user = get_jwt_identity()
        user_id = current_user["user_id"]
        data = request.json
        chat_id = data.get("chat_id")
        message_text = data.get("text")

        if not message_text or not chat_id:
            return jsonify({"error": "Chat ID and message text are required"}), 400

        user_message, ai_message = message_service.process_message(chat_id, user_id, message_text)
        if not user_message or not ai_message:
            return jsonify({"error": "Chat not found"}), 404

        return jsonify({
            "user_message": user_message,
            "ai_message": ai_message
        }), 200

    return chat_bp