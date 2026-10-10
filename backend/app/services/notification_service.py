from sqlalchemy.orm import Session
from app.models import Notification, Student
from typing import List

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(self, user_id: int, title: str, message: str, 
                           type: str = 'info') -> Notification:
        notif = Notification(user_id=user_id, title=title, message=message, type=type)
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(notif)
        return notif
    
    def get_notifications(self, user_id: int, unread_only: bool = False) -> List[Notification]:
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.is_read == False)
        return query.order_by(Notification.created_at.desc()).all()
    
    def mark_read(self, notification_id: int, user_id: int) -> bool:
        notif = self.db.query(Notification).filter(
            Notification.id == notification_id, 
            Notification.user_id == user_id
        ).first()
        if not notif:
            return False
        notif.is_read = True
        self.db.commit()
        return True
    
    def mark_all_read(self, user_id: int) -> int:
        updated = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        self.db.commit()
        return updated
    
    def get_unread_count(self, user_id: int) -> int:
        return self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
    
    def send_low_attendance_notification(self, student_id: int, percentage: float):
        """Create notification for low attendance."""
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if student and student.user_id:
            title = "Low Attendance Warning"
            message = f"Your overall attendance is {percentage:.1f}%, which is below the required threshold."
            self.create_notification(student.user_id, title, message, type='warning')
    
    async def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email notification via SMTP."""
        # Placeholder for real email sending
        print(f"Sending email to {to_email}: {subject}")
        return True
