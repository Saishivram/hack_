from functools import wraps
from flask import request, jsonify, current_app
import jwt
from bson.objectid import ObjectId
from models.db import get_db
from datetime import datetime, timedelta
import os

# Get secret key from environment variable
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')

def generate_token(user_data):
    """Generate JWT token for authenticated users."""
    try:
        payload = {
            'user_id': str(user_data['_id']),
            'username': user_data['username'],
            'role': user_data['role'],
            'exp': datetime.utcnow() + timedelta(days=1)  # Token expires in 1 day
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return token
    except Exception as e:
        print(f"Token generation error: {str(e)}")
        return None

def authenticate_user(username, password):
    """Authenticate a user and return a token."""
    try:
        db = get_db()
        user = db.users.find_one({'username': username})
        
        if user and user.check_password(password):
            token = generate_token(user)
            return token
        return None
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        return None

# =========================
# Token Required Decorator
# =========================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(" ")[1] if "Bearer" in auth_header else auth_header
            except IndexError:
                return jsonify({"error": "Invalid token format"}), 401

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            # Decode token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            
            # Get user from database
            db = get_db()
            current_user = db.users.find_one({'_id': ObjectId(data['user_id'])})
            if not current_user:
                return jsonify({"error": "Invalid token"}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 401

        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(" ")[1] if "Bearer" in auth_header else auth_header
            except IndexError:
                return jsonify({"error": "Invalid token format"}), 401

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            # Decode token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            
            # Get user from database
            db = get_db()
            current_user = db.users.find_one({'_id': ObjectId(data['user_id'])})
            if not current_user:
                return jsonify({"error": "Invalid token"}), 401
                
            # Check if user is admin
            if current_user['role'] != 'admin':
                return jsonify({"error": "Admin privileges required"}), 403
                
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 401

        return f(current_user, *args, **kwargs)
    return decorated

def doctor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(" ")[1] if "Bearer" in auth_header else auth_header
            except IndexError:
                return jsonify({"error": "Invalid token format"}), 401

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            # Decode token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            
            # Get user from database
            db = get_db()
            current_user = db.users.find_one({'_id': ObjectId(data['user_id'])})
            if not current_user:
                return jsonify({"error": "Invalid token"}), 401
                
            # Check if user is doctor
            if current_user['role'] != 'doctor':
                return jsonify({"error": "Doctor privileges required"}), 403
                
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 401

        return f(current_user, *args, **kwargs)
    return decorated
