from datetime import timedelta

class Config:
    MONGO_URI = "mongodb://localhost:27017/chatDatabase"
    JWT_SECRET_KEY = "your_jwt_secret_key"  # Change this to a secure key
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    DEBUG = True