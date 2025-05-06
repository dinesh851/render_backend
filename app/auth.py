# app/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app import models, schemas
from app.database import get_db
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

import smtplib
from email.message import EmailMessage

def send_otp_email(otp):
    user_email = settings.user_email
    user_password = settings.user_password 

    recipient_list = [
        'dineshkumar31116@gmail.com',
        'wintark222@gmail.com',
        'namachissnv@gmail.com'
    ]
    for recipient in recipient_list:
        msg = EmailMessage()
        msg['Subject'] = 'Your OTP Code'
        msg['From'] = user_email
        msg['To'] = recipient
        msg.set_content(f'{otp} is your verification code.')

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(user_email, user_password)
                smtp.send_message(msg)
            print(f'Email sent to {recipient}')
        except Exception as e:
            print(f'Failed to send to {recipient}: {e}')




# Add this function if missing
async def get_current_patient(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
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

# ... rest of your auth.py code ...
# Add this to your existing auth.py file
async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None or not payload.get("is_admin"):
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    admin = db.query(models.Admin).filter(models.Admin.username == username).first()
    if admin is None:
        raise credentials_exception
    return admin