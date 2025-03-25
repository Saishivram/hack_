from flask import Blueprint, request, jsonify
from bson import ObjectId
from models.db import get_db
from datetime import datetime
from routes.user_routes import token_required

patient_bp = Blueprint('patients', __name__)

@patient_bp.route('/', methods=['GET'])
@token_required
def get_patients(current_user):
    """Get all patients."""
    try:
        db = get_db()
        query = {}
        
        # If doctor, only show their patients
        if current_user['role'] == 'doctor':
            query['doctor_id'] = str(current_user['_id'])
            
        patients = list(db.patients.find(query))
        for patient in patients:
            patient['_id'] = str(patient['_id'])
            if 'doctor_id' in patient:
                patient['doctor_id'] = str(patient['doctor_id'])
        return jsonify(patients), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/', methods=['POST'])
@token_required
def add_patient(current_user):
    """Add a new patient."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        required_fields = ['name', 'email', 'phone', 'address', 'date_of_birth']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        # If doctor is adding patient, set doctor_id
        if current_user['role'] == 'doctor':
            data['doctor_id'] = str(current_user['_id'])
        elif 'doctor_id' in data:
            # If admin is adding patient with specific doctor
            data['doctor_id'] = str(data['doctor_id'])
            
        # Add creation timestamp
        data['created_at'] = datetime.utcnow()
        
        db = get_db()
        # Check if email already exists
        if db.patients.find_one({'email': data['email']}):
            return jsonify({'message': 'Patient with this email already exists'}), 400
            
        result = db.patients.insert_one(data)
        return jsonify({
            'message': 'Patient added successfully',
            '_id': str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/<patient_id>', methods=['PUT'])
@token_required
def update_patient(current_user, patient_id):
    """Update patient information."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        db = get_db()
        query = {'_id': ObjectId(patient_id)}
        
        # If doctor, only allow updating their own patients
        if current_user['role'] == 'doctor':
            query['doctor_id'] = str(current_user['_id'])
            
        # Don't allow changing doctor_id if current user is a doctor
        if current_user['role'] == 'doctor' and 'doctor_id' in data:
            return jsonify({'message': 'Unauthorized: Cannot change patient\'s doctor'}), 403
            
        # If email is being updated, check it doesn't conflict
        if 'email' in data:
            existing = db.patients.find_one({'email': data['email'], '_id': {'$ne': ObjectId(patient_id)}})
            if existing:
                return jsonify({'message': 'Another patient with this email already exists'}), 400
                
        result = db.patients.update_one(query, {'$set': data})
        
        if result.modified_count:
            return jsonify({'message': 'Patient updated successfully'}), 200
        return jsonify({'message': 'Patient not found or unauthorized'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/<patient_id>', methods=['DELETE'])
@token_required
def delete_patient(current_user, patient_id):
    """Delete a patient."""
    try:
        db = get_db()
        query = {'_id': ObjectId(patient_id)}
        
        # If doctor, only allow deleting their own patients
        if current_user['role'] == 'doctor':
            query['doctor_id'] = str(current_user['_id'])
            
        # Check if patient has any appointments
        if db.appointments.find_one({'patient_id': ObjectId(patient_id)}):
            return jsonify({'message': 'Cannot delete patient with existing appointments'}), 400
            
        result = db.patients.delete_one(query)
        
        if result.deleted_count:
            return jsonify({'message': 'Patient deleted successfully'}), 200
        return jsonify({'message': 'Patient not found or unauthorized'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
