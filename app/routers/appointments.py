# app/routers/appointments.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.auth import get_current_patient, get_current_admin
from app.crud import create_appointment, get_appointments_by_patient, cancel_appointment

router = APIRouter()

@router.post("/", response_model=schemas.AppointmentResponse)
def create_new_appointment(
    appointment: schemas.AppointmentCreate,
    current_patient: models.Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Create a new appointment - patients can only create with waiting_approval status"""
    try:
        db_appointment = create_appointment(db, appointment, current_patient.id)
        return db_appointment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.AppointmentResponse])
def read_appointments(
    current_patient: models.Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Get all appointments for the current patient"""
    return get_appointments_by_patient(db, current_patient.id)

@router.put("/{appointment_id}/cancel", response_model=schemas.AppointmentResponse)
def cancel_patient_appointment(
    appointment_id: str,
    current_patient: models.Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Cancel appointment - only patients can cancel their own appointments"""
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.patient_id != current_patient.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this appointment")

    if appointment.status not in ["waiting_approval", "approved"]:
        raise HTTPException(status_code=400, detail="Cannot cancel appointment at this stage")

    appointment.status = "cancelled"
    db.commit()
    db.refresh(appointment)

    return appointment

# Admin-only endpoints
@router.get("/admin/all", response_model=List[schemas.AppointmentResponse])
def get_all_appointments(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin)
):
    """Get all appointments - admin only"""
    query = db.query(models.Appointment)
    
    if status:
        query = query.filter(models.Appointment.status == status)
    
    appointments = query.offset(skip).limit(limit).all()
    return appointments

@router.put("/{appointment_id}/approve", response_model=schemas.AppointmentResponse)
def approve_appointment(
    appointment_id: str,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin)
):
    """Approve appointment - admin only"""
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.status != "waiting_approval":
        raise HTTPException(status_code=400, detail="Only waiting appointments can be approved")

    appointment.status = "approved"
    db.commit()
    db.refresh(appointment)

    return appointment

@router.put("/{appointment_id}/done", response_model=schemas.AppointmentResponse)
def mark_appointment_done(
    appointment_id: str,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin)
):
    """Mark appointment as done - admin only"""
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.status != "approved":
        raise HTTPException(status_code=400, detail="Only approved appointments can be marked as done")

    appointment.status = "done"
    db.commit()
    db.refresh(appointment)

    return appointment

@router.put("/{appointment_id}/cancel-admin", response_model=schemas.AppointmentResponse)
def cancel_appointment_admin(
    appointment_id: str,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin)
):
    """Cancel appointment - admin only"""
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.status == "done":
        raise HTTPException(status_code=400, detail="Cannot cancel completed appointments")

    appointment.status = "cancelled"
    db.commit()
    db.refresh(appointment)

    return appointment