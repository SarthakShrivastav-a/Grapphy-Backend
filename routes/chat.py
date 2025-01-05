from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.chat import Chat
from werkzeug.utils import secure_filename
from datetime import datetime
import boto3
import os
from botocore.exceptions import ClientError

chat_bp = Blueprint('chat', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_chat_routes(db, message_service):
    # Initialize S3 client
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
    except Exception as e:
        print(f"Failed to initialize S3 client: {str(e)}")
        raise

    def upload_to_s3(file, filename):
        """Helper function to handle S3 upload with error handling"""
        try:
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                return None, "File size exceeds maximum limit of 5MB"

            # Upload to S3
            s3.upload_fileobj(
                file,
                os.getenv('S3_BUCKET_NAME'),
                filename,
                ExtraArgs={
                    'ContentType': file.content_type
                }
            )
            
            # Generate URL
            file_url = f"https://{os.getenv('S3_BUCKET_NAME')}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{filename}"
            return file_url, None

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                return None, "S3 bucket does not exist"
            elif error_code == 'AccessDenied':
                return None, "Access denied to S3 bucket"
            else:
                return None, f"S3 upload failed: {str(e)}"
        except Exception as e:
            return None, f"Unexpected error during upload: {str(e)}"

    @chat_bp.route('/create_chat', methods=['POST'])
    @jwt_required()
    def create_chat():
        try:
            current_user = get_jwt_identity()
            user_id = current_user["user_id"]
            
            # Validate request
            if not request.form and not request.files:
                return jsonify({"error": "No data provided"}), 400
            
            topic = request.form.get("topic", "New Chat")
            
            # Handle file upload
            file_url = None
            if 'file' in request.files:
                file = request.files['file']
                
                # Validate file
                if file.filename == '':
                    return jsonify({"error": "No selected file"}), 400
                
                if not allowed_file(file.filename):
                    return jsonify({"error": "File type not allowed"}), 400
                
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                
                # Upload to S3
                file_url, error = upload_to_s3(file, unique_filename)
                if error:
                    return jsonify({"error": error}), 400

            # Create chat with optional image URL
            try:
                chat = Chat(user_id, topic, file_url)
                db.chats.insert_one(chat.to_dict())
            except Exception as e:
                # If chat creation fails but file was uploaded, we could implement cleanup here
                return jsonify({"error": f"Failed to create chat: {str(e)}"}), 500
            
            return jsonify({
                "chat_id": chat.chat_id,
                "img_url": file_url,
                "topic": topic
            }), 201

        except Exception as e:
            return jsonify({
                "error": "Failed to process request",
                "details": str(e)
            }), 500

    # [Rest of the routes remain the same...]

    # Keep other existing routes unchanged
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

    @chat_bp.route('/check', methods=['GET'])
    def check_health():
        return "Working Asshole"

    return chat_bp