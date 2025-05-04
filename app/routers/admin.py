from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.auth import get_current_admin

router = APIRouter()

@router.post("/", response_model=schemas.AdminBase)
def create_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    db_admin = models.Admin(
        username=admin.username,
        hashed_password=admin.password,  # Should be hashed in production
        is_superadmin=admin.is_superadmin
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin