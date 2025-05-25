# app/routers/admin_auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from app import schemas, models
from app.auth import get_current_admin
from app.database import get_db
from app.config import settings

router = APIRouter()

def create_admin_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "is_admin": True})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@router.post("/admin/login", response_model=schemas.Token)
def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Admin login endpoint"""
    admin = db.query(models.Admin).filter(
        models.Admin.username == form_data.username
    ).first()
    
    if not admin or admin.hashed_password != form_data.password:  # In production, use proper password hashing
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_admin_access_token(data={"sub": admin.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/admin/register", response_model=schemas.AdminBase)
def create_admin(
    admin: schemas.AdminCreate, 
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)  # Only existing admin can create new admin
):
    """Create new admin - requires existing admin authentication"""
    
    # Check if admin username already exists
    existing_admin = db.query(models.Admin).filter(
        models.Admin.username == admin.username
    ).first()
    
    if existing_admin:
        raise HTTPException(
            status_code=400,
            detail="Admin username already registered"
        )
    
    db_admin = models.Admin(
        username=admin.username,
        hashed_password=admin.password,  # Should be hashed in production
        is_superadmin=admin.is_superadmin
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin