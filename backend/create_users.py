from pymongo import MongoClient
from datetime import datetime
from werkzeug.security import generate_password_hash

# MongoDB Configuration
MONGODB_URI = 'mongodb://localhost:27017/'
DB_NAME = 'doctor_assistant'

def create_user(db, username, password, email, role="doctor"):
    # Check if user already exists
    if db.users.find_one({"username": username}):
        print(f"User {username} already exists")
        return
    
    # Create user document
    user = {
        "username": username,
        "password_hash": generate_password_hash(password),
        "email": email,
        "role": role,
        "created_at": datetime.utcnow()
    }
    
    # Insert into database
    result = db.users.insert_one(user)
    print(f"Created user {username} with role {role}")
    return result.inserted_id

def main():
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        
        # Create admin user
        create_user(
            db,
            username="admin",
            password="admin123",
            email="admin@hospital.com",
            role="admin"
        )
        
        # Create a doctor user
        create_user(
            db,
            username="doctor1",
            password="doctor123",
            email="doctor1@hospital.com",
            role="doctor"
        )
        
        print("Users created successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    main() 