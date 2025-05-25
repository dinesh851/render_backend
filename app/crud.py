# app/crud.py
from datetime import datetime
from sqlalchemy.orm import Session
from app import models, schemas
import random
import string

def get_patient(db: Session, patient_id: str):
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def generate_patient_id(db: Session) -> str:
    """Generate a unique 7-character patient ID (P + 6 random chars/digits)"""
    while True:
        # First character 'p', next 6 random (lowercase letters + digits)
        random_part = ''.join(random.choices(
            string.ascii_lowercase + string.digits,  # a-z + 0-9
            k=6
        ))
        patient_id = f"p{random_part}"  # e.g., "p1a3b7c"

        # Check if ID exists
        if not db.query(models.Patient).filter(models.Patient.id == patient_id).first():
            return patient_id

def create_patient(db: Session, patient_data: schemas.PatientCreate):
    """Create a new patient with generated ID"""
    patient_id = generate_patient_id(db)
    db_patient = models.Patient(
        id=patient_id,
        **patient_data.model_dump()
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def update_patient(db: Session, patient_id: str, patient_update: schemas.PatientCreate):
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return None
    for key, value in patient_update.model_dump().items():
        setattr(db_patient, key, value)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def get_doctor(db: Session, doctor_id: int):
    return db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()

def get_doctors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Doctor).offset(skip).limit(limit).all()

def time_to_slot_index(hour: int, minute: int = 0) -> int:
    """
    Convert time to slot index (1-16)
    Assuming slots are:
    9:00-9:30 = slot1, 9:30-10:00 = slot2, ..., 16:30-17:00 = slot16
    """
    if hour < 9 or hour > 16:
        raise ValueError("Hour must be between 9 and 16")
    
    if hour == 16 and minute > 30:
        raise ValueError("Last slot ends at 17:00")
    
    # Calculate slot based on 30-minute intervals
    slot_index = (hour - 9) * 2 + 1
    if minute >= 30:
        slot_index += 1
    
    return slot_index

def is_slot_available(db: Session, doctor_id: int, appointment_datetime: datetime) -> bool:
    """Check if a specific time slot is available for booking"""
    
    # Get slot index from appointment time
    try:
        slot_index = time_to_slot_index(appointment_datetime.hour, appointment_datetime.minute)
    except ValueError:
        return False
    
    # Check doctor availability for that date
    availability = db.query(models.DoctorAvailability).filter(
        models.DoctorAvailability.doctor_id == doctor_id,
        models.DoctorAvailability.date == appointment_datetime.date()
    ).first()

    if not availability:
        return False

    # Check if the specific slot is available
    slot_attr = f"slot{slot_index}"
    is_slot_open = getattr(availability, slot_attr, False)
    
    if not is_slot_open:
        return False
    
    # Check if slot is already booked
    existing_appointment = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == doctor_id,
        models.Appointment.appointment_datetime == appointment_datetime,
        models.Appointment.status.in_(["waiting_approval", "approved"])
    ).first()
    
    return existing_appointment is None

def generate_appointment_id(db: Session) -> str:
    """Generate a unique 6-character appointment ID"""
    while True:
        appointment_id = ''.join(random.choices(
            string.ascii_lowercase + string.digits,
            k=6
        ))
        
        # Check if ID exists
        if not db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first():
            return appointment_id

def create_appointment(db: Session, appointment: schemas.AppointmentCreate, patient_id: str):
    """Create a new appointment with validation"""
    
    # Check if doctor exists
    doctor = get_doctor(db, appointment.doctor_id)
    if not doctor:
        raise ValueError("Doctor not found")
    
    # Check if slot is available
    if not is_slot_available(db, appointment.doctor_id, appointment.appointment_datetime):
        raise ValueError("Selected time slot is not available")
    
    # Generate unique appointment ID
    appointment_id = generate_appointment_id(db)
    
    # Create appointment with waiting_approval status
    db_appointment = models.Appointment(
        id=appointment_id,
        patient_id=patient_id,
        doctor_id=appointment.doctor_id,
        appointment_datetime=appointment.appointment_datetime,
        notes=appointment.notes,
        status="waiting_approval"  # Patients can only create with this status
    )
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def get_appointments_by_patient(db: Session, patient_id: str):
    return db.query(models.Appointment).filter(
        models.Appointment.patient_id == patient_id
    ).order_by(models.Appointment.created_at.desc()).all()

def cancel_appointment(db: Session, appointment_id: str):
    db_appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()
    if not db_appointment:
        return None
    db_appointment.status = "cancelled"
    db.commit()
    db.refresh(db_appointment)
    return db_appointment