from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson import ObjectId

appointment_bp = Blueprint('appointment', __name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['doctor_assistant']

# Get all appointments
@appointment_bp.route('/', methods=['GET'])
def get_appointments():
    appointments = list(db.appointments.find({}))
    for appointment in appointments:
        appointment['_id'] = str(appointment['_id'])
    return jsonify(appointments)

# Get appointment by ID
@appointment_bp.route('/<string:appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    appointment = db.appointments.find_one({"_id": ObjectId(appointment_id)})
    if appointment:
        appointment['_id'] = str(appointment['_id'])
        return jsonify(appointment)
    return jsonify({"error": "Appointment not found"}), 404

# Add a new appointment
@appointment_bp.route('/add', methods=['POST'])
def add_appointment():
    data = request.json
    appointment_id = db.appointments.insert_one(data).inserted_id
    return jsonify({"message": "Appointment added successfully", "appointment_id": str(appointment_id)})

# Update appointment details
@appointment_bp.route('/update/<string:appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    data = request.json
    db.appointments.update_one({"_id": ObjectId(appointment_id)}, {"$set": data})
    return jsonify({"message": "Appointment updated successfully"})

# Delete an appointment
@appointment_bp.route('/delete/<string:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    result = db.appointments.delete_one({"_id": ObjectId(appointment_id)})
    if result.deleted_count == 1:
        return jsonify({"message": "Appointment deleted successfully"})
    return jsonify({"error": "Appointment not found"}), 404
