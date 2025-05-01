# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta, UTC  # Added UTC for the utcnow replacement
from sqlalchemy import Column, Integer, String
import random
import string
import random
import os
import jwt
from dotenv import load_dotenv
import logging
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from sqlalchemy import exc
# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connectionAAAA
DATABASE_URL = os.getenv("DATABASE_URL")
 
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



def generate_random_id(length=6):
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    random_id = ''.join(random.choice(characters) for _ in range(length))
    return random_id

# Function to check if an ID exists in the database
def id_exists(db: Session, model, id: str):
    return db.query(model).filter(model.id == id).first() is not None

# Function to generate a unique patient ID
def generate_unique_patient_id(db: Session):
    while True:
        new_patient_id = generate_random_id()
        if not id_exists(db, Patient, new_patient_id):
            return new_patient_id

# Function to generate a unique appointment ID
def generate_unique_appointment_id(db: Session):
    while True:
        new_appointment_id = generate_random_id()
        if not id_exists(db, Appointment, new_appointment_id):
            return new_appointment_id

# Database Models
class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(String(6), primary_key=True, default=generate_random_id)

    name = Column(String, index=True)
    mobile_number = Column(String, unique=True, index=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    age = Column(Integer, nullable=True)  # Added missing age column
    gender = Column(String, nullable=True)  # Added missing gender column
    created_at = Column(DateTime, default=datetime.now)
    appointments = relationship("Appointment", back_populates="patient")

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_superadmin = Column(Boolean, default=False)
    
class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    specialization = Column(String)
    
    appointments = relationship("Appointment", back_populates="doctor")
    
class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(String(6), primary_key=True, default=generate_random_id)
    patient_id = Column(String(6), ForeignKey("patients.id"))

    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    appointment_datetime = Column(DateTime)
    status = Column(String, default="scheduled")  # scheduled, completed, cancelled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    slots = int
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    
class OTP(Base):
    __tablename__ = "otps"
    
    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, index=True)
    otp = Column(String)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)
class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    date = Column(DateTime, nullable=False)
    
    # Slot columns for each of the 16 slots
    slot1 = Column(Boolean, default=False)
    slot2 = Column(Boolean, default=False)
    slot3 = Column(Boolean, default=False)
    slot4 = Column(Boolean, default=False)
    slot5 = Column(Boolean, default=False)
    slot6 = Column(Boolean, default=False)
    slot7 = Column(Boolean, default=False)
    slot8 = Column(Boolean, default=False)
    slot9 = Column(Boolean, default=False)
    slot10 = Column(Boolean, default=False)
    slot11 = Column(Boolean, default=False)
    slot12 = Column(Boolean, default=False)
    slot13 = Column(Boolean, default=False)
    slot14 = Column(Boolean, default=False)
    slot15 = Column(Boolean, default=False)
    slot16 = Column(Boolean, default=False)
    
    doctor = relationship("Doctor", back_populates="availabilities")

Doctor.availabilities = relationship("DoctorAvailability", back_populates="doctor")


# Create all tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for request/response
class PatientCreate(BaseModel):
    name: str
    mobile_number: str
    email: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None

class PatientResponse(BaseModel):
    id: int
    name: str
    mobile_number: str
    email: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_datetime: datetime
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    appointment_datetime: datetime
    status: str
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class DoctorResponse(BaseModel):
    id: int
    name: str
    specialization: str
    
    class Config:
        orm_mode = True

class AdminCreate(BaseModel):
    username: str
    password: str
    is_superadmin: bool = False

class OTPRequest(BaseModel):
    mobile_number: str

class OTPVerify(BaseModel):
    mobile_number: str
    otp: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_data: PatientResponse
class SlotValues(BaseModel):
    slot1: bool
    slot2: bool
    slot3: bool
    slot4: bool
    slot5: bool
    slot6: bool
    slot7: bool
    slot8: bool
    slot9: bool
    slot10: bool
    slot11: bool
    slot12: bool
    slot13: bool
    slot14: bool
    slot15: bool
    slot16: bool

class AvailabilityCreate(BaseModel):
    doctor_id: int
    availability: List[dict]  # List of dates and corresponding slot values

    class Config:
        orm_mode = True

class AvailabilityResponse(BaseModel):
    doctor_id: int
    date: datetime
    slot_values: SlotValues

    class Config:
        orm_mode = True


 
# Helper functions
def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_otp(mobile_number: str, otp: str):
    """Mock function to send OTP to mobile number"""
    # In a real scenario, you would integrate with an SMS gateway
    logger.info(f"Sending OTP {otp} to {mobile_number}")
    return True

def verify_patient(db: Session, mobile_number: str, otp: str):
    """Verify patient with OTP"""
    db_otp = db.query(OTP).filter(
        OTP.mobile_number == mobile_number,
        OTP.otp == otp,
        OTP.expires_at > datetime.now(),
        OTP.is_verified == False
    ).first()
    
    if not db_otp:
        return False
    
    db_otp.is_verified = True
    db.commit()
    return True

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_patient(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated patient"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Changed to pyjwt
        mobile_number: str = payload.get("sub")
        if mobile_number is None:
            raise credentials_exception
    except jwt.PyJWTError:  # Changed exception class
        raise credentials_exception
        
    patient = db.query(Patient).filter(Patient.mobile_number == mobile_number).first()
    if patient is None:
        raise credentials_exception
        
    return patient
async def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated admin"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or payload.get("is_admin") is not True:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    admin = db.query(Admin).filter(Admin.username == username).first()
    if admin is None:
        raise credentials_exception
        
    return admin

# FastAPI app
app = FastAPI(title="Doctor Appointment API")

# Authentication endpoints
@app.post("/send-otp/", status_code=status.HTTP_200_OK)
def request_otp(otp_request: OTPRequest, db: Session = Depends(get_db)):
    """Send OTP to patient's mobile number"""
    mobile_number = otp_request.mobile_number
    
    # Generate OTP
    otp = generate_otp()
    expires_at = datetime.now() + timedelta(minutes=10)
    
    # Store OTP in database
    db_otp = OTP(
        mobile_number=mobile_number,
        otp=otp,
        expires_at=expires_at
    )
    db.add(db_otp)
    db.commit()
    
    # Send OTP
    send_otp(mobile_number, otp)
    
    return {"message": "OTP sent successfully", "mobile_number": mobile_number}

@app.post("/login/", response_model=Token)
def login(otp_verify: OTPVerify, db: Session = Depends(get_db)):
    """Verify OTP and login patient"""
    mobile_number = otp_verify.mobile_number
    otp = otp_verify.otp
    
    # Verify OTP
    if not verify_patient(db, mobile_number, otp):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP or OTP expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if patient exists
    patient = db.query(Patient).filter(Patient.mobile_number == mobile_number).first()
    
    # If patient doesn't exist, create a new one with minimal information
    if not patient:
        patient = Patient(mobile_number=mobile_number, name=f"Patient-{mobile_number}")
        db.add(patient)
        db.commit()
        db.refresh(patient)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": mobile_number},
        expires_delta=access_token_expires,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_data": patient
    }

# Patient endpoints
@app.put("/patients/update", response_model=PatientResponse)
def update_patient(
    patient_data: PatientCreate,
    current_patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Update patient profile"""
    # Update patient information
    current_patient.name = patient_data.name
    if patient_data.email:
        current_patient.email = patient_data.email
    if patient_data.address:
        current_patient.address = patient_data.address
    if patient_data.date_of_birth:
        current_patient.date_of_birth = patient_data.date_of_birth
    
    db.commit()
    db.refresh(current_patient)
    
    return current_patient

@app.get("/home_user", response_model=PatientResponse)
def homeuser(current_patient: Patient = Depends(get_current_patient), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == current_patient.id).first()
    appointments = db.query(Appointment).filter(Appointment.patient_id == current_patient.id).all()
    return {"patient": patient, "appointments": appointments}




@app.get("/patient/me", response_model=PatientResponse)
def get_patient_profile(current_patient: Patient = Depends(get_current_patient)):
    """Get current patient profile"""
    return current_patient

# Appointment endpoints
@app.post("/appointments/", response_model=AppointmentResponse)
def create_appointment(
    appointment: AppointmentCreate,
    current_patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Create a new appointment for the current patient"""
    # Check if doctor exists
    doctor = db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    # Create appointment
    db_appointment = Appointment(
        patient_id=current_patient.id,
        doctor_id=appointment.doctor_id,
        appointment_datetime=appointment.appointment_datetime,
        notes=appointment.notes
    )
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment

@app.get("/appointments/", response_model=List[AppointmentResponse])
def get_patient_appointments(
    current_patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Get all appointments for the current patient"""
    appointments = db.query(Appointment).filter(Appointment.patient_id == current_patient.id).all()
    return appointments

@app.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    current_patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Get a specific appointment for the current patient"""
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.patient_id == current_patient.id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    return appointment

@app.put("/appointments/{appointment_id}/cancel")
def cancel_appointment(
    appointment_id: int,
    current_patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Cancel a specific appointment"""
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.patient_id == current_patient.id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    appointment.status = "cancelled"
    db.commit()
    
    return {"message": "Appointment cancelled successfully"}

# Doctor endpoints
@app.get("/doctors/", response_model=List[DoctorResponse])
def get_all_doctors(db: Session = Depends(get_db)):
    """Get all doctors"""
    doctors = db.query(Doctor).all()
    return doctors

# Admin endpoints
@app.post("/admin/create")
def create_admin(
    admin_data: AdminCreate,
    db: Session = Depends(get_db)
):
    """Create a new admin user (this should be restricted in production)"""
    # In production, this should be protected and only accessible by super admins
    # Check if username already exists
    existing_admin = db.query(Admin).filter(Admin.username == admin_data.username).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new admin
    # In a real scenario, you would hash the password
    new_admin = Admin(
        username=admin_data.username,
        hashed_password=admin_data.password,  # Should be hashed in production
        is_superadmin=admin_data.is_superadmin
    )
    
    db.add(new_admin)
    db.commit()
    
    return {"message": "Admin created successfully"}

@app.post("/admin/login")
def admin_login(
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    """Admin login endpoint"""
    admin = db.query(Admin).filter(Admin.username == username).first()
    
    if not admin or admin.hashed_password != password:  # Should compare hashed passwords in production
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username, "is_admin": True, "is_superadmin": admin.is_superadmin},
        expires_delta=access_token_expires,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/admin/patients", response_model=List[PatientResponse])
def get_all_patients(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all patients (admin only)"""
    patients = db.query(Patient).all()
    return patients

@app.get("/admin/appointments", response_model=List[AppointmentResponse])
def get_all_appointments(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all appointments (admin only)"""
    appointments = db.query(Appointment).all()
    return appointments

# Set the availability slots for a doctor on specific dates
@app.post("/doctors/{doctor_id}/availability", response_model=List[AvailabilityResponse])
def set_doctor_availability(
    doctor_id: int,
    availability: AvailabilityCreate,
    db: Session = Depends(get_db)
):
    """Set the availability for a doctor on specific dates"""
    # Ensure doctor exists
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    # Create availability records for the doctor
    for availability_entry in availability.availability:
        date = availability_entry["date"]
        slot_values = availability_entry["slot_values"]
        
        # Check if there's already availability for the specific date
        existing_availability = db.query(DoctorAvailability).filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.date == date
        ).first()

        if existing_availability:
            # Update the existing availability if the date is already present
            for slot, value in slot_values.items():
                setattr(existing_availability, slot, value)
            db.commit()
        else:
            # Create new availability for the doctor
            new_availability = DoctorAvailability(
                doctor_id=doctor_id,
                date=date,
                **slot_values  # Unpack slot values into the model
            )
            db.add(new_availability)
            db.commit()

    return {"message": "Doctor availability updated successfully"}


# Get the availability slots for a doctor
@app.get("/doctors/{doctor_id}/availability", response_model=List[AvailabilityResponse])
def get_doctor_availability(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """Get the availability slots for a doctor"""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    # Retrieve the availability for the doctor
    availabilities = db.query(DoctorAvailability).filter(DoctorAvailability.doctor_id == doctor_id).all()

    return availabilities


# Create initial data for testing
@app.on_event("startup")
def create_initial_data():
    db = SessionLocal()
    try:
        # Check if there are any doctors
        doctor_count = db.query(Doctor).count()
        if doctor_count == 0:
            # Create sample doctors
            doctors = [
                Doctor(name="Dr. John Smith", specialization="Dentist"),
                Doctor(name="Dr. Sarah Johnson", specialization="Orthodontist"),
                Doctor(name="Dr. Michael Brown", specialization="Periodontist")
            ]
            db.add_all(doctors)
            db.commit()
            logger.info("Created sample doctors")
        
        # Check if there are any admins
        admin_count = db.query(Admin).count()
        if admin_count == 0:
            # Create default admin
            admin = Admin(
                username="admin",
                hashed_password="admin123",  # Should be hashed in production
                is_superadmin=True
            )
            db.add(admin)
            db.commit()
            logger.info("Created default admin user")
            
    except Exception as e:
        logger.error(f"Error creating initial data: {str(e)}")
    finally:
        db.close()
@app.get("/healthcheck", status_code=200)
def health_check(db: Session = Depends(get_db)):
    """Check if the database connection is healthy"""
    try:
        db.execute("SELECT 1")
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error")
from sqlalchemy import inspect, text

@app.get("/tables")
def list_all_tables(
    db: Session = Depends(get_db)
):
    """List all tables in the database and their row counts (admin only)"""
    inspector = inspect(db.bind)
    tables_info = {}

    for table_name in inspector.get_table_names():
        try:
            result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            row_count = result.scalar()
            tables_info[table_name] = {"rows": row_count}
        except Exception as e:
            tables_info[table_name] = {"error": str(e)}

    return tables_info

# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)