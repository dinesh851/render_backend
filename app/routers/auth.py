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
from app.crud import create_patient


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

# @router.post("/send-otp", response_model=schemas.OTPRequest)
# def send_otp(request: schemas.OTPRequest, db: Session = Depends(get_db)):
#     otp = generate_otp()
#     expires_at = datetime.utcnow() + timedelta(minutes=10)
    
#     db_otp = models.OTP(
#         mobile_number=request.mobile_number,
#         otp=otp,
#         expires_at=expires_at
#     )
#     db.add(db_otp)
#     db.commit()
#     # send_otp_email(int(otp))
#     logger.info(f"OTP sent to {request.mobile_number}: {otp}")
#     print(f"OTP sent to {request.mobile_number}: {otp}")
#     return {"mobile_number": request.mobile_number}

@router.post("/send-otp", response_model=schemas.OTPSuccessResponse)
def send_otp(request: schemas.OTPRequest, db: Session = Depends(get_db)):
    otp = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
   
    print(f"Generated OTP: {otp}, Expires at: {expires_at}")
    existing_otp = db.query(models.OTP).filter(
        models.OTP.mobile_number == request.mobile_number,
        models.OTP.expires_at > datetime.utcnow()
    ).first()

    if existing_otp:
        # Resend by updating
        existing_otp.otp = otp
        existing_otp.expires_at = expires_at
        db.commit()
        logger.info(f"OTP resent to {request.mobile_number}: {otp}")
    else:
        # New OTP entry
        db_otp = models.OTP(
            mobile_number=request.mobile_number,
            otp=otp,
            expires_at=expires_at
        )
        db.add(db_otp)
        db.commit()
        logger.info(f"OTP sent to {request.mobile_number}: {otp}")

    print(f"OTP sent to {request.mobile_number}: {otp}")
    send_otp_email(int(otp))

    return {
        "success": True,
        "message": "OTP sent successfully.",
        "mobile_number": request.mobile_number
    }

@router.post("/login", response_model=schemas.Token)
def login(verify: schemas.OTPVerify, db: Session = Depends(get_db)):
    # Debug: Print all unexpired OTPs for this mobile number
    print("Checking OTPs for:", verify.mobile_number)
    all_otps = db.query(models.OTP).filter(
        models.OTP.mobile_number == verify.mobile_number,
        models.OTP.expires_at > datetime.utcnow()
    ).all()
    print("All unexpired OTPs:", [(o.otp, o.is_verified, o.expires_at) for o in all_otps])
    
    # Verify OTP
    db_otp = db.query(models.OTP).filter(
        models.OTP.mobile_number == verify.mobile_number,
        models.OTP.otp == verify.otp,
        models.OTP.expires_at > datetime.utcnow(),
        models.OTP.is_verified == False
    ).first()
    
    print("Found matching OTP:", db_otp)
    
    if not db_otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP or OTP already used/expired"
        )
    
    # Mark OTP as verified
    db_otp.is_verified = True
    
    # Handle patient creation
    patient = db.query(models.Patient).filter(
        models.Patient.mobile_number == verify.mobile_number
    ).first()
    
    if not patient:
        patient_data = schemas.PatientCreate(
            name=f"Patient-{verify.mobile_number}",
            mobile_number=verify.mobile_number
        )
        patient = create_patient(db, patient_data)
    
    db.commit()
    
    access_token = create_access_token(data={"sub": verify.mobile_number})
    return {"access_token": access_token, "token_type": "bearer"}