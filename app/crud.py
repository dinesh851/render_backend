from sqlalchemy.orm import Session
from app import models, schemas
import random
import string
def get_patient(db: Session, patient_id: str):
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def generate_patient_id(db: Session) -> str:
    """Generate a unique 7-character patient ID (P + 6 random chars/digits)"""
    while True:
        # First character 'P', next 6 random (uppercase letters + digits)
        random_part = ''.join(random.choices(
            string.ascii_lowercase + string.digits,  # A-Z + 0-9
            k=6
        ))
        patient_id = f"p{random_part}"  # e.g., "P1A3B7C"

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

def create_appointment(db: Session, appointment: schemas.AppointmentCreate, patient_id: str):
    db_appointment = models.Appointment(**appointment.model_dump(), patient_id=patient_id)
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def get_appointments_by_patient(db: Session, patient_id: str):
    return db.query(models.Appointment).filter(models.Appointment.patient_id == patient_id).all()

def cancel_appointment(db: Session, appointment_id: str):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not db_appointment:
        return None
    db_appointment.status = "cancelled"
    db.commit()
    db.refresh(db_appointment)
    return db_appointment