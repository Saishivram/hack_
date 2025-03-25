from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models.db import get_db
import jwt
from datetime import datetime, timedelta
from functools import wraps
import os

auth_bp = Blueprint('auth', __name__)

# Secret key for JWT - in production, use environment variable
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            db = get_db()
            current_user = db.users.find_one({'_id': data['user_id']})
            if not current_user:
                return jsonify({'message': 'Invalid token'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Check if required fields are present
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        db = get_db()
        
        # Check if username already exists
        if db.users.find_one({'username': data['username']}):
            return jsonify({'message': 'Username already exists'}), 400
        
        # Check if email already exists
        if db.users.find_one({'email': data['email']}):
            return jsonify({'message': 'Email already exists'}), 400
        
        # Hash the password
        hashed_password = generate_password_hash(data['password'])
        
        # Create new user
        new_user = {
            'username': data['username'],
            'email': data['email'],
            'password': hashed_password,
            'role': data['role'],
            'created_at': datetime.utcnow()
        }
        
        result = db.users.insert_one(new_user)
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Error during registration: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'message': 'Missing username or password'}), 400
        
        db = get_db()
        user = db.users.find_one({'username': data['username']})
        
        if not user or not check_password_hash(user['password'], data['password']):
            return jsonify({'message': 'Invalid username or password'}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': str(user['_id']),
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, SECRET_KEY)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error during login: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    try:
        user_data = {
            'id': str(current_user['_id']),
            'username': current_user['username'],
            'email': current_user['email'],
            'role': current_user['role']
        }
        return jsonify(user_data), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching profile: {str(e)}'}), 500 