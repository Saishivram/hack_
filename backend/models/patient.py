from flask import Blueprint, request, jsonify
from pymongo import MongoClient

patient_bp = Blueprint('patient', __name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['doctor_assistant']

# Get all patients
@patient_bp.route('/', methods=['GET'])
def get_patients():
    patients = list(db.patients.find({}))
    for patient in patients:
        patient['_id'] = str(patient['_id'])
    return jsonify(patients)

# Add a new patient
@patient_bp.route('/add', methods=['POST'])
def add_patient():
    data = request.json
    db.patients.insert_one(data)
    return jsonify({"message": "Patient added successfully"})

# Update patient data
@patient_bp.route('/update/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    data = request.json
    db.patients.update_one({"patient_id": patient_id}, {"$set": data})
    return jsonify({"message": "Patient updated successfully"})

# Delete a patient
@patient_bp.route('/delete/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    db.patients.delete_one({"patient_id": patient_id})
    return jsonify({"message": "Patient deleted successfully"})
