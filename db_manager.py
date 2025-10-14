import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from utils.database import (
    Patient, Appointment, MedicalRecord, Prescription, DiseasePrediction,
    SessionLocal, init_db
)

class DatabaseManager:
    """Manages all database operations for the healthcare system."""
    
    def __init__(self):
        # Initialize database tables
        init_db()
    
    def get_db(self):
        """Get a database session"""
        return SessionLocal()
    
    # Patient management methods
    def add_patient(self, patient_data):
        """Add a new patient to the database."""
        db = self.get_db()
        try:
            patient_data['id'] = str(uuid.uuid4())
            patient_data['created_at'] = datetime.now().isoformat()
            
            patient = Patient(**patient_data)
            db.add(patient)
            db.commit()
            db.refresh(patient)
            return patient.id
        finally:
            db.close()
    
    def get_patients(self):
        """Get all patients."""
        db = self.get_db()
        try:
            patients = db.query(Patient).all()
            return [self._patient_to_dict(p) for p in patients]
        finally:
            db.close()
    
    def get_patient_by_id(self, patient_id):
        """Get a specific patient by ID."""
        db = self.get_db()
        try:
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            return self._patient_to_dict(patient) if patient else None
        finally:
            db.close()
    
    def update_patient(self, patient_id, updated_data):
        """Update patient information."""
        db = self.get_db()
        try:
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            if patient:
                for key, value in updated_data.items():
                    setattr(patient, key, value)
                patient.updated_at = datetime.now().isoformat()
                db.commit()
                return True
            return False
        finally:
            db.close()
    
    def delete_patient(self, patient_id):
        """Delete a patient from the database."""
        db = self.get_db()
        try:
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            if patient:
                db.delete(patient)
                db.commit()
                return True
            return False
        finally:
            db.close()
    
    def search_patients(self, query):
        """Search patients by name, email, or phone."""
        db = self.get_db()
        try:
            query = query.lower()
            patients = db.query(Patient).filter(
                (Patient.name.ilike(f'%{query}%')) |
                (Patient.email.ilike(f'%{query}%')) |
                (Patient.phone.ilike(f'%{query}%'))
            ).all()
            return [self._patient_to_dict(p) for p in patients]
        finally:
            db.close()
    
    # Appointment management methods
    def add_appointment(self, appointment_data):
        """Add a new appointment."""
        db = self.get_db()
        try:
            appointment_data['id'] = str(uuid.uuid4())
            appointment_data['created_at'] = datetime.now().isoformat()
            
            appointment = Appointment(**appointment_data)
            db.add(appointment)
            db.commit()
            db.refresh(appointment)
            return appointment.id
        finally:
            db.close()
    
    def get_appointments(self):
        """Get all appointments."""
        db = self.get_db()
        try:
            appointments = db.query(Appointment).all()
            return [self._appointment_to_dict(a) for a in appointments]
        finally:
            db.close()
    
    def get_appointments_by_date(self, date):
        """Get appointments for a specific date."""
        db = self.get_db()
        try:
            appointments = db.query(Appointment).filter(Appointment.date == date).all()
            return [self._appointment_to_dict(a) for a in appointments]
        finally:
            db.close()
    
    def get_appointments_by_patient(self, patient_id):
        """Get appointments for a specific patient."""
        db = self.get_db()
        try:
            appointments = db.query(Appointment).filter(Appointment.patient_id == patient_id).all()
            return [self._appointment_to_dict(a) for a in appointments]
        finally:
            db.close()
    
    def update_appointment_status(self, appointment_id, status):
        """Update appointment status."""
        db = self.get_db()
        try:
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            if appointment:
                appointment.status = status
                appointment.updated_at = datetime.now().isoformat()
                db.commit()
                return True
            return False
        finally:
            db.close()
    
    def delete_appointment(self, appointment_id):
        """Delete an appointment."""
        db = self.get_db()
        try:
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            if appointment:
                db.delete(appointment)
                db.commit()
                return True
            return False
        finally:
            db.close()
    
    # Medical records methods
    def add_medical_record(self, record_data):
        """Add a new medical record."""
        db = self.get_db()
        try:
            record_data['id'] = str(uuid.uuid4())
            record_data['created_at'] = datetime.now().isoformat()
            
            record = MedicalRecord(**record_data)
            db.add(record)
            db.commit()
            db.refresh(record)
            return record.id
        finally:
            db.close()
    
    def get_medical_records(self):
        """Get all medical records."""
        db = self.get_db()
        try:
            records = db.query(MedicalRecord).all()
            return [self._medical_record_to_dict(r) for r in records]
        finally:
            db.close()
    
    def get_medical_records_by_patient(self, patient_id):
        """Get medical records for a specific patient."""
        db = self.get_db()
        try:
            records = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).all()
            return [self._medical_record_to_dict(r) for r in records]
        finally:
            db.close()
    
    # Prescription methods
    def add_prescription(self, prescription_data):
        """Add a new prescription."""
        db = self.get_db()
        try:
            prescription_data['id'] = str(uuid.uuid4())
            prescription_data['created_at'] = datetime.now().isoformat()
            
            prescription = Prescription(**prescription_data)
            db.add(prescription)
            db.commit()
            db.refresh(prescription)
            return prescription.id
        finally:
            db.close()
    
    def get_prescriptions(self):
        """Get all prescriptions."""
        db = self.get_db()
        try:
            prescriptions = db.query(Prescription).all()
            return [self._prescription_to_dict(p) for p in prescriptions]
        finally:
            db.close()
    
    def get_prescriptions_by_patient(self, patient_id):
        """Get prescriptions for a specific patient."""
        db = self.get_db()
        try:
            prescriptions = db.query(Prescription).filter(Prescription.patient_id == patient_id).all()
            return [self._prescription_to_dict(p) for p in prescriptions]
        finally:
            db.close()
    
    def update_prescription_status(self, prescription_id, status):
        """Update prescription status."""
        db = self.get_db()
        try:
            prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
            if prescription:
                prescription.status = status
                prescription.updated_at = datetime.now().isoformat()
                db.commit()
                return True
            return False
        finally:
            db.close()
    
    # Disease prediction methods
    def add_disease_prediction(self, prediction_data):
        """Add a disease prediction result."""
        db = self.get_db()
        try:
            prediction_data['id'] = str(uuid.uuid4())
            prediction_data['created_at'] = datetime.now().isoformat()
            
            prediction = DiseasePrediction(**prediction_data)
            db.add(prediction)
            db.commit()
            db.refresh(prediction)
            return prediction.id
        finally:
            db.close()
    
    def get_disease_predictions(self):
        """Get all disease predictions."""
        db = self.get_db()
        try:
            predictions = db.query(DiseasePrediction).all()
            return [self._prediction_to_dict(p) for p in predictions]
        finally:
            db.close()
    
    def get_predictions_by_patient(self, patient_id):
        """Get predictions for a specific patient."""
        db = self.get_db()
        try:
            predictions = db.query(DiseasePrediction).filter(DiseasePrediction.patient_id == patient_id).all()
            return [self._prediction_to_dict(p) for p in predictions]
        finally:
            db.close()
    
    # Helper methods to convert SQLAlchemy objects to dictionaries
    def _patient_to_dict(self, patient):
        if not patient:
            return None
        return {
            'id': patient.id,
            'name': patient.name,
            'email': patient.email,
            'phone': patient.phone,
            'date_of_birth': patient.date_of_birth,
            'gender': patient.gender,
            'blood_group': patient.blood_group,
            'emergency_contact': patient.emergency_contact,
            'address': patient.address,
            'medical_history': patient.medical_history,
            'current_medications': patient.current_medications,
            'insurance_info': patient.insurance_info,
            'age': patient.age,
            'created_at': patient.created_at,
            'updated_at': patient.updated_at
        }
    
    def _appointment_to_dict(self, appointment):
        if not appointment:
            return None
        return {
            'id': appointment.id,
            'patient_id': appointment.patient_id,
            'patient_name': appointment.patient_name,
            'doctor': appointment.doctor,
            'department': appointment.department,
            'date': appointment.date,
            'time': appointment.time,
            'type': appointment.type,
            'status': appointment.status,
            'notes': appointment.notes,
            'created_at': appointment.created_at,
            'updated_at': appointment.updated_at
        }
    
    def _medical_record_to_dict(self, record):
        if not record:
            return None
        return {
            'id': record.id,
            'patient_id': record.patient_id,
            'record_type': record.record_type,
            'title': record.title,
            'date': record.date,
            'doctor': record.doctor,
            'department': record.department,
            'priority': record.priority,
            'status': record.status,
            'description': record.description,
            'findings': record.findings,
            'recommendations': record.recommendations,
            'lab_values': record.lab_values,
            'file_name': record.file_name,
            'file_type': record.file_type,
            'file_size': record.file_size,
            'document_type': record.document_type,
            'created_at': record.created_at,
            'updated_at': record.updated_at
        }
    
    def _prescription_to_dict(self, prescription):
        if not prescription:
            return None
        return {
            'id': prescription.id,
            'patient_id': prescription.patient_id,
            'doctor': prescription.doctor,
            'medication_name': prescription.medication_name,
            'dosage': prescription.dosage,
            'frequency': prescription.frequency,
            'quantity': prescription.quantity,
            'refills_remaining': prescription.refills_remaining,
            'duration': prescription.duration,
            'route': prescription.route,
            'instructions': prescription.instructions,
            'indication': prescription.indication,
            'warnings': prescription.warnings,
            'interactions': prescription.interactions,
            'date_prescribed': prescription.date_prescribed,
            'status': prescription.status,
            'created_at': prescription.created_at,
            'updated_at': prescription.updated_at
        }
    
    def _prediction_to_dict(self, prediction):
        if not prediction:
            return None
        return {
            'id': prediction.id,
            'patient_id': prediction.patient_id,
            'symptoms': prediction.symptoms,
            'primary_prediction': prediction.primary_prediction,
            'confidence': prediction.confidence,
            'all_predictions': prediction.all_predictions,
            'symptom_count': prediction.symptom_count,
            'severity': prediction.severity,
            'duration': prediction.duration,
            'additional_notes': prediction.additional_notes,
            'prediction_date': prediction.prediction_date,
            'created_at': prediction.created_at
        }
