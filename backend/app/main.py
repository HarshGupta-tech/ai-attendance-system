from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.core.config import settings
import os
from contextlib import asynccontextmanager
from app.api import auth, students, subjects, attendance, dashboard, reports, users, notifications, settings_api, audit_logs

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
    yield

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(subjects.router, prefix="/api/subjects", tags=["Subjects"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["Settings"])
app.include_router(audit_logs.router, prefix="/api/audit-logs", tags=["Audit Logs"])

@app.get("/")
def read_root():
    return {"message": settings.APP_NAME + " API", "version": settings.APP_VERSION}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
