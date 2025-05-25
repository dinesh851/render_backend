# app/routers/doctors.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
from app import schemas, models
from app.database import get_db
from app.crud import get_doctors
from app.auth import get_current_admin

router = APIRouter()

@router.get("/", response_model=List[schemas.DoctorResponse])
def read_doctors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all doctors"""
    return get_doctors(db, skip=skip, limit=limit)

@router.post("/{doctor_id}/availability")
def set_doctor_availability(
    doctor_id: int,
    availability_data: schemas.BulkAvailabilityCreate,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin)
):
    """Set doctor availability for multiple dates - admin only"""
    
    # Check if doctor exists
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    results = []
    
    for availability_item in availability_data.availability:
        # Parse date string to date object
        try:
            availability_date = datetime.strptime(availability_item.date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {availability_item.date}")
        
        # Check if availability already exists for this doctor and date
        existing_availability = db.query(models.DoctorAvailability).filter(
            models.DoctorAvailability.doctor_id == doctor_id,
            models.DoctorAvailability.date == availability_date
        ).first()
        
        if existing_availability:
            # Update existing availability
            slot_values = availability_item.slot_values.model_dump()
            for slot_name, slot_value in slot_values.items():
                setattr(existing_availability, slot_name, slot_value)
            
            db.commit()
            db.refresh(existing_availability)
            results.append({
                "date": availability_item.date,
                "action": "updated",
                "availability_id": existing_availability.id
            })
        else:
            # Create new availability
            new_availability = models.DoctorAvailability(
                doctor_id=doctor_id,
                date=availability_date,
                **availability_item.slot_values.model_dump()
            )
            db.add(new_availability)
            db.commit()
            db.refresh(new_availability)
            results.append({
                "date": availability_item.date,
                "action": "created",
                "availability_id": new_availability.id
            })
    
    return {
        "message": "Doctor availability updated successfully",
        "doctor_id": doctor_id,
        "results": results
    }

@router.get("/{doctor_id}/availability")
def get_doctor_availability(
    doctor_id: int,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """Get doctor availability for specified date range"""
    
    # Check if doctor exists
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    query = db.query(models.DoctorAvailability).filter(
        models.DoctorAvailability.doctor_id == doctor_id
    )
    
    # Filter by date range if provided
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(models.DoctorAvailability.date >= start_date_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(models.DoctorAvailability.date <= end_date_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
    
    availabilities = query.order_by(models.DoctorAvailability.date).all()
    
    # Format response
    formatted_availability = []
    for availability in availabilities:
        slots = {}
        for i in range(1, 17):
            slot_name = f"slot{i}"
            slots[slot_name] = getattr(availability, slot_name, False)
        
        formatted_availability.append({
            "id": availability.id,
            "date": availability.date.isoformat(),
            "slots": slots
        })
    
    return {
        "doctor_id": doctor_id,
        "doctor_name": doctor.name,
        "availability": formatted_availability
    }

@router.delete("/{doctor_id}/availability/{date}")
def delete_doctor_availability(
    doctor_id: int,
    date: str,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin)
):
    """Delete doctor availability for a specific date - admin only"""
    
    try:
        availability_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    availability = db.query(models.DoctorAvailability).filter(
        models.DoctorAvailability.doctor_id == doctor_id,
        models.DoctorAvailability.date == availability_date
    ).first()
    
    if not availability:
        raise HTTPException(status_code=404, detail="Availability not found for this date")
    
    db.delete(availability)
    db.commit()
    
    return {"message": f"Availability deleted for doctor {doctor_id} on {date}"}