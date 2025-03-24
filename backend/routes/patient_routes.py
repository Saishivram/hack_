from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime   
from utils.ai_analyzer import analyze_patient_data




patient_bp = Blueprint('patient', __name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['doctor_assistant']

# Get all patients
@patient_bp.route('/', methods=['GET'])
def get_patients():
    patients = list(db.patients.find({}))
    for patient in patients:
        patient['_id'] = str(patient['_id'])
    return jsonify(patients)

# Get a patient by ID
@patient_bp.route('/<string:patient_id>', methods=['GET'])
def get_patient(current_user, patient_id):
    patient = db.patients.find_one({"_id": ObjectId(patient_id)})
    if patient:
        return jsonify({"patient": patient}), 200
    else:
        return jsonify({"error": "Patient not found"}), 404

# Add a new patient
@patient_bp.route('/add', methods=['POST'])
def add_patient():
    data = request.json
    admin_id = data.get('created_by')
    if not admin_id:
        return jsonify({"error": "Admin ID required"}), 400

    patient_id = db.patients.insert_one(data).inserted_id
    return jsonify({"message": "Patient added successfully", "patient_id": str(patient_id)})


# Update patient data
@patient_bp.route('/update/<string:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    data = request.json
    db.patients.update_one({"_id": ObjectId(patient_id)}, {"$set": data})
    return jsonify({"message": "Patient updated successfully"})

# Delete a patient
@patient_bp.route('/delete/<string:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    result = db.patients.delete_one({"_id": ObjectId(patient_id)})
    if result.deleted_count == 1:
        return jsonify({"message": "Patient deleted successfully"})
    return jsonify({"error": "Patient not found"}), 404

# Update Medications & Conditions - Doctor Route
@patient_bp.route('/update-medications/<string:patient_id>', methods=['POST'])
def update_medications(patient_id):
    data = request.json
    update_data = {
        "medications": data.get('medications'),
        "current_conditions": data.get('current_conditions'),
        "doctor_notes": data.get('doctor_notes')
    }

    result = db.patients.update_one({"_id": ObjectId(patient_id)}, {"$set": update_data})
    if result.matched_count == 1:
        return jsonify({"message": "Medications and conditions updated successfully"})
    else:
        return jsonify({"error": "Patient not found"}), 404