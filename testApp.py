from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
import google.generativeai as genai

genai.configure(api_key="")
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/chatDatabase"
db = PyMongo(app).db

model = genai.GenerativeModel("gemini-1.5-flash")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])

def chat():
    user_input = request.json.get("input", "").strip()
    
    if user_input:

        db.chats.insert_one({"sender": "User", "message": user_input})

        ai_response = model.generate_content(user_input)
        ai_message = ai_response.text.strip()

        db.chats.insert_one({"sender": "AI", "message": ai_message})
        return jsonify({"user_message": user_input, "ai_message": ai_message}), 200

    return jsonify({"success": False, "message": "Invalid input!"}), 400

@app.route('/get_chats', methods=['GET'])
def get_chats():
    # Retrieve all chats from MongoDB
    chats = list(db.chats.find({}, {"_id": 0, "sender": 1, "message": 1}))
    return jsonify({"chats": chats}), 200

if __name__ == "__main__":
    app.run(debug=True)
