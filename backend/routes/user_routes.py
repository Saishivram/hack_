from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from bson import ObjectId
from db import mongo

user_bp = Blueprint('user', __name__)

# Secret key for JWT - in production, use environment variable
SECRET_KEY = 'your-secret-key'

@user_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(k in data for k in ['username', 'email', 'password', 'role']):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Validate role
        if data['role'] not in ['doctor', 'admin']:
            return jsonify({'message': 'Invalid role. Must be either doctor or admin'}), 400
        
        # Check if username or email already exists
        if mongo.db.users.find_one({'username': data['username']}):
            return jsonify({'message': 'Username already exists'}), 400
        if mongo.db.users.find_one({'email': data['email']}):
            return jsonify({'message': 'Email already exists'}), 400
        
        # Hash password and create user
        hashed_password = generate_password_hash(data['password'])
        user = {
            'username': data['username'],
            'email': data['email'],
            'password': hashed_password,
            'role': data['role'],
            'created_at': datetime.utcnow()
        }
        
        result = mongo.db.users.insert_one(user)
        user_id = str(result.inserted_id)
        
        # Generate token
        token = jwt.encode({
            'user_id': user_id,
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(days=1)
        }, SECRET_KEY)
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'username': user['username'],
            'role': user['role'],
            '_id': user_id
        }), 201
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({'message': 'An error occurred during registration'}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['username', 'password']):
            return jsonify({'message': 'Missing username or password'}), 400
        
        user = mongo.db.users.find_one({'username': data['username']})
        if not user:
            return jsonify({'message': 'Invalid username or password'}), 401
            
        if not check_password_hash(user['password'], data['password']):
            return jsonify({'message': 'Invalid username or password'}), 401
        
        # Generate token
        token = jwt.encode({
            'user_id': str(user['_id']),
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(days=1)
        }, SECRET_KEY)
        
        return jsonify({
            'token': token,
            'username': user['username'],
            'role': user['role']
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'message': 'An error occurred during login'}), 500

def token_required(f):
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
            
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = mongo.db.users.find_one({'_id': ObjectId(data['user_id'])})
            if not current_user:
                return jsonify({'message': 'Invalid token'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'message': 'Token validation failed'}), 401
            
        return f(current_user, *args, **kwargs)
    
    decorated.__name__ = f.__name__
    return decorated

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({
        'username': current_user['username'],
        'email': current_user['email'],
        'role': current_user['role']
    }), 200

@user_bp.route('/doctors', methods=['GET'])
@token_required
def get_doctors(current_user):
    try:
        # Only admin can access this endpoint
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Unauthorized access'}), 403
            
        doctors = list(mongo.db.users.find({'role': 'doctor'}))
        # Convert ObjectId to string for JSON serialization
        for doctor in doctors:
            doctor['_id'] = str(doctor['_id'])
            # Remove password from response
            doctor.pop('password', None)
        
        return jsonify(doctors), 200
    except Exception as e:
        print(f"Error fetching doctors: {str(e)}")
        return jsonify({'message': 'An error occurred while fetching doctors'}), 500

@user_bp.route('/doctors/<doctor_id>', methods=['DELETE'])
@token_required
def delete_doctor(current_user, doctor_id):
    try:
        # Only admin can delete doctors
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Unauthorized access'}), 403
            
        result = mongo.db.users.delete_one({
            '_id': ObjectId(doctor_id),
            'role': 'doctor'
        })
        
        if result.deleted_count:
            return jsonify({'message': 'Doctor deleted successfully'}), 200
        return jsonify({'message': 'Doctor not found'}), 404
    except Exception as e:
        print(f"Error deleting doctor: {str(e)}")
        return jsonify({'message': 'An error occurred while deleting doctor'}), 500 