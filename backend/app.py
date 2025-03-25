from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from routes.user_routes import user_bp
from routes.patient_routes import patient_bp
from routes.appointment_routes import appointment_bp
from db import mongo
import os

app = Flask(__name__)

# Configure trailing slashes
app.url_map.strict_slashes = False

# Configure CORS properly
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "expose_headers": ["Authorization"],
        "allow_credentials": True
    }
})

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/doctor_assistant"
mongo.init_app(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(patient_bp, url_prefix='/api/patients')
app.register_blueprint(appointment_bp, url_prefix='/api/appointments')

# Serve frontend static files
@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'login.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

# Test database connection
@app.route('/api/test-connection')
def test_connection():
    try:
        # Test MongoDB connection
        mongo.db.command('ping')
        return jsonify({"message": "Database connection successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
