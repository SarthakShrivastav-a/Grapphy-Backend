from datetime import datetime
from bson.objectid import ObjectId
import bcrypt

class User:
    def __init__(self, username=None, password=None, google_id=None, email=None):
        self.username = username
        self.user_id = str(ObjectId())
        self.created_at = datetime.utcnow().isoformat()
        self.google_id = google_id
        self.email = email
        if password:
            self.password_hash = self._hash_password(password)

    def _hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "password_hash": getattr(self, "password_hash", None),
            "google_id": self.google_id,
            "email": self.email,
            "created_at": self.created_at
        }
