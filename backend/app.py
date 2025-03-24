from flask import Flask
from flask_cors import CORS
from routes.patient_routes import patient_bp
from routes.user_routes import user_bp
from routes.appointment_routes import appointment_bp
from pymongo import MongoClient
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['doctor_assistant']

# Register Blueprints
app.register_blueprint(patient_bp, url_prefix='/api/patients')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(appointment_bp, url_prefix='/api/appointments')

if __name__ == "__main__":
    app.run(debug=True)
