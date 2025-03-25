from flask import Blueprint, request, jsonify
from bson import ObjectId
from models.db import get_db
from datetime import datetime
from routes.user_routes import token_required

appointment_bp = Blueprint('appointments', __name__)

@appointment_bp.route('/', methods=['GET'])
@token_required
def get_appointments(current_user):
    """Get all appointments."""
    try:
        db = get_db()
        query = {}
        
        # If doctor, only show their appointments
        if current_user['role'] == 'doctor':
            query['doctor_id'] = str(current_user['_id'])
            
        appointments = list(db.appointments.find(query))
        for appointment in appointments:
            appointment['_id'] = str(appointment['_id'])
            if 'patient_id' in appointment:
                appointment['patient_id'] = str(appointment['patient_id'])
            if 'doctor_id' in appointment:
                appointment['doctor_id'] = str(appointment['doctor_id'])
        return jsonify(appointments), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointment_bp.route('/<appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    """Get a single appointment by ID."""
    try:
        db = get_db()
        appointment = db.appointments.find_one({'_id': ObjectId(appointment_id)})
        if appointment:
            appointment['_id'] = str(appointment['_id'])
            if 'patient_id' in appointment:
                appointment['patient_id'] = str(appointment['patient_id'])
            return jsonify(appointment), 200
        return jsonify({'message': 'Appointment not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointment_bp.route('/', methods=['POST'])
@token_required
def create_appointment(current_user):
    """Create a new appointment."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        required_fields = ['patient_id', 'doctor_id', 'date', 'time', 'reason']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        # Convert IDs to ObjectId
        data['patient_id'] = ObjectId(data['patient_id'])
        data['doctor_id'] = ObjectId(data['doctor_id'])
        
        # Add creation timestamp and status
        data['created_at'] = datetime.utcnow()
        data['status'] = 'scheduled'
        
        # If current user is a doctor, ensure they can only create appointments for themselves
        if current_user['role'] == 'doctor' and str(data['doctor_id']) != str(current_user['_id']):
            return jsonify({'message': 'Unauthorized: Cannot create appointments for other doctors'}), 403
        
        db = get_db()
        result = db.appointments.insert_one(data)
        return jsonify({
            'message': 'Appointment created successfully',
            '_id': str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointment_bp.route('/<appointment_id>', methods=['PUT'])
@token_required
def update_appointment(current_user, appointment_id):
    """Update appointment information."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        db = get_db()
        query = {'_id': ObjectId(appointment_id)}
        
        # If doctor, only allow updating their own appointments
        if current_user['role'] == 'doctor':
            query['doctor_id'] = ObjectId(str(current_user['_id']))
        
        # Convert IDs if present
        if 'patient_id' in data:
            data['patient_id'] = ObjectId(data['patient_id'])
        if 'doctor_id' in data:
            data['doctor_id'] = ObjectId(data['doctor_id'])
            # Doctors can't reassign appointments to other doctors
            if current_user['role'] == 'doctor' and str(data['doctor_id']) != str(current_user['_id']):
                return jsonify({'message': 'Unauthorized: Cannot reassign appointments to other doctors'}), 403
        
        result = db.appointments.update_one(query, {'$set': data})
        
        if result.modified_count:
            return jsonify({'message': 'Appointment updated successfully'}), 200
        return jsonify({'message': 'Appointment not found or unauthorized'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointment_bp.route('/<appointment_id>', methods=['DELETE'])
@token_required
def delete_appointment(current_user, appointment_id):
    """Delete an appointment."""
    try:
        db = get_db()
        query = {'_id': ObjectId(appointment_id)}
        
        # If doctor, only allow deleting their own appointments
        if current_user['role'] == 'doctor':
            query['doctor_id'] = ObjectId(str(current_user['_id']))
        
        result = db.appointments.delete_one(query)
        
        if result.deleted_count:
            return jsonify({'message': 'Appointment deleted successfully'}), 200
        return jsonify({'message': 'Appointment not found or unauthorized'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
