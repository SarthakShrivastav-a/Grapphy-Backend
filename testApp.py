from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes and all origins
CORS(app, supports_credentials=True)

# AWS S3 configuration
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

# MongoDB configuration
mongo_client = MongoClient(os.getenv('MONGO_URI'))
db = mongo_client['image_db']
images_collection = db['images']

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to get all images
@app.route('/images', methods=['GET'])
def get_images():
    try:
        images = list(images_collection.find())
        # Convert ObjectId to string
        for image in images:
            image['_id'] = str(image['_id'])
        return jsonify(images)
    except Exception as e:
        print(f"Error fetching images: {str(e)}")
        return jsonify([])

# Route to upload image
@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            
            # Upload to S3
            s3.upload_fileobj(
                file,
                os.getenv('S3_BUCKET_NAME'),
                unique_filename,
              
            )
            
            # Generate URL
            file_url = f"https://{os.getenv('S3_BUCKET_NAME')}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{unique_filename}"
            
            # Save to MongoDB
            images_collection.insert_one({
                'filename': unique_filename,
                'original_filename': filename,
                'url': file_url,
                'uploaded_at': datetime.now()
            })
            
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully',
                'url': file_url
            })
            
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)