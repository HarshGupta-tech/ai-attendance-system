from pydantic import BaseModel, ConfigDict
from datetime import datetime, date, time

class AttendanceSessionCreate(BaseModel):
    subject_id: int
    course_id: int | None = None
    semester: int | None = None
    section: str | None = None
    date: date
    start_time: time
    end_time: time
    late_threshold_minutes: int = 15

class AttendanceSessionUpdate(BaseModel):
    status: str | None = None
    end_time: time | None = None
    late_threshold_minutes: int | None = None

class AttendanceSessionResponse(BaseModel):
    id: int
    subject_id: int
    subject_name: str | None = None
    subject_code: str | None = None
    course_id: int | None = None
    semester: int | None = None
    section: str | None = None
    date: date
    start_time: time
    end_time: time
    late_threshold_minutes: int
    status: str
    created_by: int | None = None
    created_by_name: str | None = None
    total_present: int = 0
    total_late: int = 0
    total_absent: int = 0
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AttendanceRecordResponse(BaseModel):
    id: int
    session_id: int
    student_id: int
    student_name: str | None = None
    student_roll: str | None = None
    check_in_time: datetime | None = None
    status: str
    confidence: float | None = None
    verification_method: str | None = None
    device_info: str | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RecognitionRequest(BaseModel):
    session_id: int
    image_data: str  # base64 encoded frame
    device_info: str | None = None

class RecognitionResult(BaseModel):
    student_id: str | None = None
    student_name: str | None = None
    confidence: float
    status: str  # recognized, unknown, already_marked, error
    message: str
    bounding_box: list[int] | None = None

class RecognitionResponse(BaseModel):
    results: list[RecognitionResult]
    frame_processed: bool = True
    timestamp: datetime
class ManualAttendanceRequest(BaseModel):
    student_id: int
    status: str

class SelfAttendanceRequest(BaseModel):
    session_code: str
    image_data: str  # base64 encoded face image
