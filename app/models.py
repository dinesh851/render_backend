from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base
import random
import string

def generate_random_id(length=6):
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


class Patient(Base):
    __tablename__ = "patients"
    
    # Changed from String(6) to String(7) to accommodate 'P' + 6 characters
    id = Column(String(7), primary_key=True, index=True)
    name = Column(String, index=True)
    mobile_number = Column(String, unique=True, index=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
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
    availabilities = relationship("DoctorAvailability", back_populates="doctor")

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(String(6), primary_key=True, default=generate_random_id)
    patient_id = Column(String(6), ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    appointment_datetime = Column(DateTime)
    status = Column(String, default="scheduled")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")

class OTP(Base):
    __tablename__ = "otps"
    
    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, index=True)
    otp = Column(String)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    date = Column(DateTime, nullable=False)
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