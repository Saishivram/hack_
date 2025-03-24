import datetime
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt()

class User(UserMixin):
    def __init__(self, user_data):
        """Initialize User object with data from MongoDB."""
        self.id = str(user_data.get("_id"))  # Convert MongoDB ObjectId to string
        self.username = user_data.get("username")
        self.email = user_data.get("email")
        self.password_hash = user_data.get("password_hash")
        self.role = user_data.get("role")  # 'doctor' or 'admin'

    @staticmethod
    def create_user(db, username, email, password, role):
        """Create a new user with a hashed password."""
        password_hash = generate_password_hash(password)  # Hash the password
        user_data = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "created_at": datetime.datetime.utcnow()
        }
        return db.users.insert_one(user_data).inserted_id

    @staticmethod
    def find_by_username(db, username):
        """Find a user by username."""
        user_data = db.users.find_one({"username": username})
        return User(user_data) if user_data else None

    @staticmethod
    def find_by_email(db, email):
        """Find a user by email."""
        user_data = db.users.find_one({"email": email})
        return User(user_data) if user_data else None

    @staticmethod
    def find_by_id(db, user_id):
        """Find a user by ID."""
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        return User(user_data) if user_data else None

    def check_password(self, password):
        """Verify the password using bcrypt."""
        return check_password_hash(self.password_hash, password)
