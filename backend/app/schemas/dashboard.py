from pydantic import BaseModel
from .attendance import AttendanceSessionResponse

class DashboardStats(BaseModel):
    total_students: int = 0
    present_today: int = 0
    absent_today: int = 0
    late_today: int = 0
    attendance_percentage: float = 0.0
    active_subjects: int = 0
    total_sessions: int = 0
    low_attendance_count: int = 0

class AttendanceTrend(BaseModel):
    date: str
    present: int
    absent: int
    late: int
    total: int

class SubjectAttendance(BaseModel):
    subject_name: str
    subject_code: str
    attendance_percentage: float
    total_sessions: int

class LowAttendanceStudent(BaseModel):
    student_id: str
    student_name: str
    course_name: str | None = None
    semester: int
    attendance_percentage: float
    total_classes: int
    present: int
    absent: int
    late: int
    risk_level: str  # safe, warning, critical

class DashboardResponse(BaseModel):
    stats: DashboardStats
    daily_trend: list[AttendanceTrend]
    weekly_trend: list[AttendanceTrend]
    subject_attendance: list[SubjectAttendance]
    low_attendance_students: list[LowAttendanceStudent]
    recent_sessions: list[AttendanceSessionResponse]
