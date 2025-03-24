from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from models.user import User
from bson import ObjectId
from ..utils.auth import authenticate_user, token_required

# ================================
# Initialize Blueprint and MongoDB
# ================================
user_bp = Blueprint('user', __name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['doctor_assistant']

# ================================
# Register a new user (Admin Only)
# ================================
@user_bp.route('/register', methods=['POST'])
@token_required
def register_user(current_user):
    """Admin creates a new user."""
    if current_user['role'] != 'admin':
        return jsonify({"error": "Unauthorized! Admin access required"}), 403

    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'doctor')

    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    if User.find_by_username(db, username):
        return jsonify({"error": "Username already exists"}), 400

    user_id = User.create_user(db, username, email, password, role)
    return jsonify({"message": "User registered successfully", "user_id": str(user_id)}), 201


# ================================
# Login user
# ================================
@user_bp.route('/login', methods=['POST'])
def login_user():
    """Authenticate and login user."""
    data = request.json
    username = data.get("username")
    password = data.get("password")

    token = authenticate_user(username, password)
    if token:
        return jsonify({"token": token}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401


# ================================
# Get all users (Admin Only)
# ================================
@user_bp.route('/', methods=['GET'])
@token_required
def get_users(current_user):
    """Retrieve all users (admin only)."""
    if current_user['role'] != 'admin':
        return jsonify({"error": "Unauthorized! Admin access required"}), 403

    users = list(db.users.find({}, {"password_hash": 0}))
    for user in users:
        user['_id'] = str(user['_id'])
    return jsonify(users), 200


# ================================
# Get user by ID (Admin/Doctor)
# ================================
@user_bp.route('/<string:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    """Retrieve a single user by ID."""
    user = db.users.find_one({"_id": ObjectId(user_id)}, {"password_hash": 0})
    if user:
        user['_id'] = str(user['_id'])
        return jsonify(user), 200
    return jsonify({"error": "User not found"}), 404


# ================================
# Update user info (Admin Only)
# ================================
@user_bp.route('/update/<string:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    """Update user information (admin only)."""
    if current_user['role'] != 'admin':
        return jsonify({"error": "Unauthorized! Admin access required"}), 403

    data = request.json
    update_data = {}

    if 'username' in data:
        update_data['username'] = data['username']
    if 'email' in data:
        update_data['email'] = data['email']
    if 'role' in data:
        update_data['role'] = data['role']

    result = db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})

    if result.modified_count == 0:
        return jsonify({"error": "No changes were made or user not found"}), 404

    return jsonify({"message": "User updated successfully"}), 200


# ================================
# Delete user (Admin Only)
# ================================
@user_bp.route('/delete/<string:user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    """Delete a user by ID (admin only)."""
    if current_user['role'] != 'admin':
        return jsonify({"error": "Unauthorized! Admin access required"}), 403

    result = db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"message": "User deleted successfully"}), 200


# ================================
# Change User Password (Self Update)
# ================================
@user_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """Allow users to change their own password."""
    data = request.json
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    # Validate current password
    user = User.find_by_username(db, current_user['username'])
    if not user or not user.check_password(current_password):
        return jsonify({"error": "Incorrect current password"}), 403

    # Update password hash
    new_password_hash = User.generate_hash(new_password)
    db.users.update_one(
        {"_id": ObjectId(current_user['_id'])},
        {"$set": {"password_hash": new_password_hash}}
    )

    return jsonify({"message": "Password updated successfully"}), 200
