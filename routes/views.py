from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def home():
    return render_template('login.html')

@views_bp.route('/signup')
def signup_page():
    return render_template('signup.html')

@views_bp.route('/chats')
@jwt_required()
def chats_page():
    return render_template('chats.html')