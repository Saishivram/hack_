from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os

# MongoDB connection string from environment variables
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'doctor_assistant')

# Global variable to store the database connection
_db = None

def init_db():
    """Initialize the database connection."""
    global _db
    try:
        client = MongoClient(MONGO_URI)
        # Test the connection
        client.admin.command('ping')
        _db = client[DB_NAME]
        print(f"Successfully connected to MongoDB database: {DB_NAME}")
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        print(f"An error occurred while connecting to MongoDB: {e}")
        raise

def get_db():
    """Get the database connection."""
    global _db
    if _db is None:
        init_db()
    return _db 