from fastapi import FastAPI
from .api import hospital,patient,appointment,billing,clinical,diagnostics,medicine,pharmacy,overall_analytics,staff
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Arogya Mitra Analytics Hub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"], # change it with react dev urls
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(hospital.router, prefix="/api/v1/hospitals", tags=["Hospital Analytics"])
app.include_router(patient.router, prefix="/api/v1/patients", tags=["Patient Analytics"])
app.include_router(appointment.router, prefix="/api/v1/appointments", tags=["Appointment Analytics"])
app.include_router(staff.router, prefix="/api/v1/staff", tags=["Staff Analytics"])
app.include_router(billing.router, prefix="/api/v1/billings", tags=["Billing Analytics"])
app.include_router(clinical.router, prefix="/api/v1/clinical", tags=["Clinical Analytics"])
app.include_router(diagnostics.router, prefix="/api/v1/diagnostics", tags=["Diagnostics Analytics"])
app.include_router(medicine.router, prefix="/api/v1/medicine", tags=["Medicine Analytics"])
app.include_router(pharmacy.router, prefix="/api/v1/pharmacy", tags=["Pharmacy Analytics"])
app.include_router(overall_analytics.router, prefix="/api/v1/summary_analytics", tags=["Overall Analytics"])



@app.get("/")
def root():
    return {"message": "Arogya Mitra Analytics Hub is Online"}