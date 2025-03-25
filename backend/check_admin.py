from pymongo import MongoClient
from werkzeug.security import generate_password_hash

# MongoDB configuration
MONGO_URI = 'mongodb://localhost:27017/'
DB_NAME = 'doctor_assistant'

def check_admin():
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        
        # Find admin user
        admin = db.users.find_one({"username": "admin"})
        
        if admin:
            print("Admin user found:")
            print(f"Username: {admin['username']}")
            print(f"Email: {admin['email']}")
            print(f"Role: {admin['role']}")
            print(f"Password Hash: {admin['password_hash']}")
            
            # Generate a new hash for comparison
            new_hash = generate_password_hash("admin123")
            print(f"\nNew Hash for 'admin123': {new_hash}")
            
            # Check if hashes match
            if admin['password_hash'] == new_hash:
                print("\nHashes match!")
            else:
                print("\nHashes don't match!")
        else:
            print("Admin user not found!")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    check_admin() 