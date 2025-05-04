from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.auth import get_current_patient
from app.crud import get_patient, update_patient

router = APIRouter()

@router.get("/me", response_model=schemas.PatientResponse)
def read_patient_me(current_patient: models.Patient = Depends(get_current_patient)):
    return current_patient

@router.put("/update", response_model=schemas.PatientResponse)
def update_patient_profile(
    patient_update: schemas.PatientCreate,
    current_patient: models.Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    updated_patient = update_patient(db, current_patient.id, patient_update)
    if not updated_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return updated_patient

