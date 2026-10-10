from pydantic import BaseModel
from datetime import datetime, date

class ReportFilter(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    student_id: int | None = None
    subject_id: int | None = None
    course_id: int | None = None
    semester: int | None = None
    section: str | None = None
    status: str | None = None

class StudentReportRow(BaseModel):
    student_id: str
    student_name: str
    roll_number: str
    total_classes: int
    present: int
    late: int
    absent: int
    excused: int
    attendance_percentage: float
    risk_level: str

class SubjectReportRow(BaseModel):
    subject_code: str
    subject_name: str
    total_sessions: int
    avg_attendance: float
    highest_attendance: float
    lowest_attendance: float

class AttendanceReportResponse(BaseModel):
    title: str
    generated_at: datetime
    filters: dict
    data: list[dict]
    summary: dict
