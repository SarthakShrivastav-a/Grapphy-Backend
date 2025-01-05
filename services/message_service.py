
# services/message_service.py
from datetime import datetime
from bson.objectid import ObjectId

class MessageService:
    def __init__(self, db, ai_service):
        self.db = db
        self.ai_service = ai_service

    def create_message(self, role, content):
        return {
            "message_id": str(ObjectId()),
            "role": role,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "text",
            "content": {"text": content}
        }

    def process_message(self, chat_id, user_id, message_text):
        chat = self.db.chats.find_one({"chat_id": chat_id, "user_id": user_id})
        if not chat:
            return None, None

        user_message = self.create_message("user", message_text)
        self.db.chats.update_one(
            {"chat_id": chat_id},
            {
                "$push": {"messages": user_message},
                "$set": {"updated_at": user_message["timestamp"]}
            }
        )

        ai_response = self.ai_service.generate_response(message_text)
        ai_message = self.create_message("assistant", ai_response)
        
        self.db.chats.update_one(
            {"chat_id": chat_id},
            {"$push": {"messages": ai_message}}
        )

        return user_message, ai_message