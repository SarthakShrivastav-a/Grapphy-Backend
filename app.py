from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS 
from flask_jwt_extended import JWTManager
from config import Config
from services.ai_service import AIService
from services.message_service import MessageService
from routes.auth import init_auth_routes
from routes.chat import init_chat_routes
from routes.views import views_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    # Initialize extensions
    mongo = PyMongo(app)
    jwt = JWTManager(app)
    
    # Initialize services
    ai_service = AIService(api_key="AIzaSyDKvJBGxmhAYjC7O5stDTBHeexdLT6VlMo") 
    message_service = MessageService(mongo.db, ai_service)

    # Register blueprints
    app.register_blueprint(views_bp)
    app.register_blueprint(init_auth_routes(mongo.db))
    app.register_blueprint(init_chat_routes(mongo.db, message_service))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()