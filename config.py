from datetime import timedelta

class Config:
    MONGO_URI = "mongodb://localhost:27017/chatDatabase"
    JWT_SECRET_KEY = "4f2a8d3f4e9c0bc8490c9fb0fd8e67ed38a5999c663ff4300cd5d78439fe981e"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_VERIFY_SUB = False 
    DEBUG = True