from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app import schemas, models
from app.database import get_db
from app.config import settings
import random
import logging
from app.auth import send_otp_email

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
logger = logging.getLogger(__name__)

def generate_otp():
    return str(random.randint(100000, 999999))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_patient(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        mobile_number: str = payload.get("sub")
        if mobile_number is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    patient = db.query(models.Patient).filter(models.Patient.mobile_number == mobile_number).first()
    if patient is None:
        raise credentials_exception
    return patient

@router.post("/send-otp", response_model=schemas.OTPRequest)
def send_otp(request: schemas.OTPRequest, db: Session = Depends(get_db)):
    otp = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    db_otp = models.OTP(
        mobile_number=request.mobile_number,
        otp=otp,
        expires_at=expires_at
    )
    db.add(db_otp)
    db.commit()
    send_otp_email(int(otp))
    logger.info(f"OTP sent to {request.mobile_number}: {otp}")
    print(f"OTP sent to {request.mobile_number}: {otp}")
    return {"mobile_number": request.mobile_number}

@router.post("/login", response_model=schemas.Token)
def login(verify: schemas.OTPVerify, db: Session = Depends(get_db)):
    db_otp = db.query(models.OTP).filter(
        models.OTP.mobile_number == verify.mobile_number,
        models.OTP.otp == verify.otp,
        models.OTP.expires_at > datetime.utcnow(),
        models.OTP.is_verified == False
    ).first()
    
    if not db_otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    db_otp.is_verified = True
    db.commit()
    
    patient = db.query(models.Patient).filter(models.Patient.mobile_number == verify.mobile_number).first()
    if not patient:
        patient = models.Patient(mobile_number=verify.mobile_number, name=f"Patient-{verify.mobile_number}")
        db.add(patient)
        db.commit()
        db.refresh(patient)
    
    access_token = create_access_token(data={"sub": verify.mobile_number})
    return {"access_token": access_token, "token_type": "bearer"}
    