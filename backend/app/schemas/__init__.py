from .auth import LoginRequest, TokenResponse, ChangePasswordRequest
from .user import UserBase, UserCreate, UserUpdate, UserResponse
from .student import StudentBase, StudentCreate, StudentUpdate, StudentResponse, StudentListResponse
from .subject import SubjectBase, SubjectCreate, SubjectUpdate, SubjectResponse
from .department import DepartmentBase, DepartmentCreate, DepartmentUpdate, DepartmentResponse
from .course import CourseBase, CourseCreate, CourseUpdate, CourseResponse
from .attendance import AttendanceSessionCreate, AttendanceSessionUpdate, AttendanceSessionResponse, AttendanceRecordResponse, RecognitionRequest, RecognitionResult, RecognitionResponse
from .dashboard import DashboardStats, AttendanceTrend, SubjectAttendance, LowAttendanceStudent, DashboardResponse
from .report import ReportFilter, StudentReportRow, SubjectReportRow, AttendanceReportResponse
from .notification import NotificationCreate, NotificationResponse
from .audit_log import AuditLogResponse, AuditLogListResponse
from .common import MessageResponse, ErrorResponse, PaginationParams
from .settings import SystemSettingResponse, SystemSettingUpdate
from .face import FaceRegistrationRequest, FaceRegistrationResponse, FaceRegistrationStatus
