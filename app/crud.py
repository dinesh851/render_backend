from sqlalchemy.orm import Session
from app import models, schemas

def get_patient(db: Session, patient_id: str):
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def create_patient(db: Session, patient: schemas.PatientCreate):
    db_patient = models.Patient(**patient.model_dump())
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