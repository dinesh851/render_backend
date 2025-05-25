from fastapi import FastAPI
from app.routers import patients, appointments, doctors, admin, auth, admin_auth
from app.database import engine, Base
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Doctor Appointment API"
)

# Include all routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin_auth.router, prefix="/auth", tags=["admin-auth"])  # Add admin auth router
app.include_router(patients.router, prefix="/patients", tags=["patients"])
app.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
app.include_router(doctors.router, prefix="/doctors", tags=["doctors"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/", tags=["root"])
def read_root():
    return {"message": "Welcome to Doctor Appointment API"}