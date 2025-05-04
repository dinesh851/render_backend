from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas
from app.database import get_db
from app.crud import get_doctors

router = APIRouter()
@router.get("/", response_model=list[schemas.AppointmentResponse])
def read_doctors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_doctors(db, skip=skip, limit=limit)