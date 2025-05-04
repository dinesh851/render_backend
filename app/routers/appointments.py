from typing import List  # Add this at the top of the file
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.auth import get_current_patient
from app.crud import create_appointment, get_appointments_by_patient, cancel_appointment

router = APIRouter()

@router.post("/", response_model=schemas.AppointmentResponse)
def create_new_appointment(
    appointment: schemas.AppointmentCreate,
    current_patient: models.Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    return create_appointment(db, appointment, current_patient.id)

@router.get("/", response_model=List[schemas.AppointmentResponse])  # Now this will work
def read_appointments(
    current_patient: models.Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    return get_appointments_by_patient(db, current_patient.id)

@router.put("/{appointment_id}/cancel", response_model=schemas.AppointmentResponse)
def cancel_patient_appointment(
    appointment_id: str,
    current_patient: models.Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    appointment = cancel_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appointment.patient_id != current_patient.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this appointment")
    return appointment