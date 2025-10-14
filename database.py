import os
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# Database setup with proper error handling
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please ensure PostgreSQL database is configured. "
        "You can create a database using the Replit Database pane."
    )

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    raise RuntimeError(f"Failed to initialize database connection: {str(e)}")

# Database Models
class Patient(Base):
    __tablename__ = 'patients'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    date_of_birth = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    blood_group = Column(String)
    emergency_contact = Column(String)
    address = Column(Text)
    medical_history = Column(Text)
    current_medications = Column(Text)
    insurance_info = Column(String)
    age = Column(Integer)
    created_at = Column(String)
    updated_at = Column(String)

class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(String, primary_key=True)
    patient_id = Column(String, nullable=False)
    patient_name = Column(String, nullable=False)
    doctor = Column(String, nullable=False)
    department = Column(String)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    type = Column(String)
    status = Column(String, nullable=False, default='Scheduled')
    notes = Column(Text)
    created_at = Column(String)
    updated_at = Column(String)

class MedicalRecord(Base):
    __tablename__ = 'medical_records'
    
    id = Column(String, primary_key=True)
    patient_id = Column(String, nullable=False)
    record_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    date = Column(String, nullable=False)
    doctor = Column(String, nullable=False)
    department = Column(String)
    priority = Column(String)
    status = Column(String)
    description = Column(Text)
    findings = Column(Text)
    recommendations = Column(Text)
    lab_values = Column(JSON)
    file_name = Column(String)
    file_type = Column(String)
    file_size = Column(Integer)
    document_type = Column(String)
    created_at = Column(String)
    updated_at = Column(String)

class Prescription(Base):
    __tablename__ = 'prescriptions'
    
    id = Column(String, primary_key=True)
    patient_id = Column(String, nullable=False)
    doctor = Column(String, nullable=False)
    medication_name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    refills_remaining = Column(Integer, default=0)
    duration = Column(String)
    route = Column(String)
    instructions = Column(Text)
    indication = Column(String)
    warnings = Column(Text)
    interactions = Column(Text)
    date_prescribed = Column(String, nullable=False)
    status = Column(String, nullable=False, default='Active')
    created_at = Column(String)
    updated_at = Column(String)

class DiseasePrediction(Base):
    __tablename__ = 'disease_predictions'
    
    id = Column(String, primary_key=True)
    patient_id = Column(String, nullable=False)
    symptoms = Column(JSON, nullable=False)
    primary_prediction = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    all_predictions = Column(JSON)
    symptom_count = Column(Integer)
    severity = Column(String)
    duration = Column(String)
    additional_notes = Column(Text)
    prediction_date = Column(String, nullable=False)
    created_at = Column(String)

# Create all tables
def init_db():
    """Initialize the database by creating all tables"""
    Base.metadata.create_all(bind=engine)

# Database helper functions
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass

def close_db(db):
    """Close database session"""
    db.close()
