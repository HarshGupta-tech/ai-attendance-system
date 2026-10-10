from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Student, AttendanceRecord, AttendanceSession, Subject
from datetime import datetime, date, timedelta
from typing import List, Dict

class DashboardService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_statistics(self) -> dict:
        today = date.today()
        
        total_students = self.db.query(Student).count()
        
        today_records = self.db.query(AttendanceRecord.status, func.count(AttendanceRecord.id))\
            .join(AttendanceSession)\
            .filter(AttendanceSession.date == today)\
            .group_by(AttendanceRecord.status).all()
            
        present_today = 0
        absent_today = 0
        late_today = 0
        
        for status, count in today_records:
            if status == 'present':
                present_today = count
            elif status == 'absent':
                absent_today = count
            elif status == 'late':
                late_today = count
                
        # Overall percentage
        total_records = self.db.query(AttendanceRecord).count()
        present_records = self.db.query(AttendanceRecord).filter(AttendanceRecord.status.in_(['present', 'late'])).count()
        overall_percentage = (present_records / total_records * 100) if total_records > 0 else 0
        
        active_subjects = self.db.query(Subject).filter(Subject.status == 'active').count()
        total_sessions = self.db.query(AttendanceSession).count()
        
        return {
            "total_students": total_students,
            "present_today": present_today,
            "absent_today": absent_today,
            "late_today": late_today,
            "overall_attendance_percentage": round(overall_percentage, 2),
            "active_subjects_count": active_subjects,
            "total_sessions": total_sessions,
            "low_attendance_students_count": len(self.get_low_attendance_students())
        }
    
    def get_daily_trend(self, days: int = 7) -> List[dict]:
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        trend = []
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            records = self.db.query(AttendanceRecord.status, func.count(AttendanceRecord.id))\
                .join(AttendanceSession)\
                .filter(AttendanceSession.date == current_date)\
                .group_by(AttendanceRecord.status).all()
                
            stats = {'date': current_date.isoformat(), 'present': 0, 'absent': 0, 'late': 0}
            for status, count in records:
                if status in stats:
                    stats[status] = count
            trend.append(stats)
            
        return trend
    
    def get_weekly_trend(self, weeks: int = 4) -> List[dict]:
        end_date = date.today()
        start_date = end_date - timedelta(weeks=weeks)
        
        trend = []
        for i in range(weeks):
            week_start = start_date + timedelta(weeks=i)
            week_end = week_start + timedelta(days=6)
            
            records = self.db.query(AttendanceRecord.status, func.count(AttendanceRecord.id))\
                .join(AttendanceSession)\
                .filter(AttendanceSession.date >= week_start, AttendanceSession.date <= week_end)\
                .group_by(AttendanceRecord.status).all()
                
            stats = {'week_start': week_start.isoformat(), 'present': 0, 'absent': 0, 'late': 0}
            for status, count in records:
                if status in stats:
                    stats[status] = count
            trend.append(stats)
            
        return trend
    
    def get_subject_attendance(self) -> List[dict]:
        subjects = self.db.query(Subject).all()
        result = []
        for subject in subjects:
            total = self.db.query(AttendanceRecord).join(AttendanceSession)\
                .filter(AttendanceSession.subject_id == subject.id).count()
            present = self.db.query(AttendanceRecord).join(AttendanceSession)\
                .filter(AttendanceSession.subject_id == subject.id, AttendanceRecord.status.in_(['present', 'late'])).count()
                
            percentage = (present / total * 100) if total > 0 else 0
            result.append({
                "subject_id": subject.id,
                "subject_code": subject.code,
                "subject_name": subject.name,
                "attendance_percentage": round(percentage, 2)
            })
        return result
    
    def get_low_attendance_students(self, threshold: float = 75.0) -> List[dict]:
        students = self.db.query(Student).all()
        result = []
        for student in students:
            total = self.db.query(AttendanceRecord).filter(AttendanceRecord.student_id == student.id).count()
            if total == 0:
                continue
                
            present = self.db.query(AttendanceRecord).filter(
                AttendanceRecord.student_id == student.id, 
                AttendanceRecord.status.in_(['present', 'late'])
            ).count()
            
            percentage = (present / total) * 100
            if percentage < threshold:
                risk = "critical" if percentage < 60 else "warning"
                result.append({
                    "student_id": student.id,
                    "student_code": student.student_id,
                    "full_name": student.full_name,
                    "attendance_percentage": round(percentage, 2),
                    "risk_level": risk
                })
        return result
    
    def get_recent_sessions(self, limit: int = 5) -> List[dict]:
        sessions = self.db.query(AttendanceSession, Subject)\
            .join(Subject)\
            .order_by(AttendanceSession.date.desc(), AttendanceSession.start_time.desc())\
            .limit(limit).all()
            
        result = []
        for session, subject in sessions:
            result.append({
                "session_id": session.id,
                "subject_code": subject.code,
                "subject_name": subject.name,
                "date": session.date.isoformat(),
                "time": session.start_time.isoformat(),
                "status": session.status
            })
        return result
