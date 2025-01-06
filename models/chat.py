from datetime import datetime
from bson.objectid import ObjectId

class Chat:
    def __init__(self, user_id,topic="New Chat", img_url=""):
        self.chat_id = str(ObjectId())
        self.user_id = user_id
        self.img_url = img_url
        self.topic = topic
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = self.created_at
        self.messages = []

    def to_dict(self):
        return {
            "chat_id": self.chat_id,
            "user_id": self.user_id,
            "img_url": self.img_url,
            "topic": self.topic,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": self.messages
        }