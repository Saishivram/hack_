from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

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

class Patient:
    def __init__(self, patient_data):
        """Initialize Patient object with data from MongoDB."""
        if patient_data is None:
            raise ValueError("Patient data cannot be None")
            
        self.id = str(patient_data.get("_id"))
        self.name = patient_data.get("name")
        self.age = patient_data.get("age")
        self.gender = patient_data.get("gender")
        self.contact_number = patient_data.get("contact_number", "")

        self.email = patient_data.get("email", "")

        self.address = patient_data.get("address", "")

        self.medical_history = patient_data.get("medical_history", [])
        self.allergies = patient_data.get("allergies", [])
        self.medications = patient_data.get("medications", [])

        self.allergies = patient_data.get("allergies", [])
        self.medications = patient_data.get("medications", [])
        self.created_at = patient_data.get("created_at", datetime.utcnow().isoformat())

        self.updated_at = patient_data.get("updated_at", datetime.utcnow().isoformat())


    @staticmethod
    def create_patient(db, patient_data):
        """Create a new patient."""
        try:
            # Add timestamps
            patient_data["created_at"] = datetime.utcnow()
            patient_data["updated_at"] = datetime.utcnow()
            
            # Insert patient into database
            result = db.patients.insert_one(patient_data)
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Failed to create patient: {str(e)}")

    @staticmethod
    def find_by_id(db, patient_id):
        """Find a patient by ID."""
        try:
            if isinstance(patient_id, str):
                patient_id = ObjectId(patient_id)
            patient_data = db.patients.find_one({"_id": patient_id})
            return Patient(patient_data) if patient_data else None
        except Exception as e:
            raise Exception(f"Failed to find patient: {str(e)}")

    @staticmethod
    def get_all_patients(db):
        """Get all patients."""
        try:
            patients = list(db.patients.find())
            return [Patient(patient).to_dict() for patient in patients]
        except Exception as e:
            raise Exception(f"Failed to get patients: {str(e)}")

    def update(self, db, update_data):
        """Update patient information."""
        try:
            update_data["updated_at"] = datetime.utcnow()
            result = db.patients.update_one(
                {"_id": ObjectId(self.id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            raise Exception(f"Failed to update patient: {str(e)}")

    def add_medical_history(self, db, history_entry):
        """Add a medical history entry."""
        try:
            history_entry["date"] = datetime.utcnow()
            result = db.patients.update_one(
                {"_id": ObjectId(self.id)},
                {
                    "$push": {"medical_history": history_entry},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            raise Exception(f"Failed to add medical history: {str(e)}")

    def update_allergies(self, db, allergies):
        """Update patient allergies."""
        try:
            result = db.patients.update_one(
                {"_id": ObjectId(self.id)},
                {
                    "$set": {
                        "allergies": allergies,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            raise Exception(f"Failed to update allergies: {str(e)}")

    def update_medications(self, db, medications):
        """Update patient medications."""
        try:
            result = db.patients.update_one(
                {"_id": ObjectId(self.id)},
                {
                    "$set": {
                        "medications": medications,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            raise Exception(f"Failed to update medications: {str(e)}")

    def to_dict(self):
        """Convert patient object to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "contact_number": self.contact_number,
            "email": self.email,
            "address": self.address,
            "medical_history": self.medical_history,
            "allergies": self.allergies,
            "medications": self.medications,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
