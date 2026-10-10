from sqlalchemy.orm import Session
from app.models import AuditLog
from datetime import date
from typing import Optional, Tuple, List

class AuditService:
    def __init__(self, db: Session):
        self.db = db
    
    def log(self, user_id: Optional[int], action: str, resource_type: Optional[str] = None,
            resource_id: Optional[str] = None, details: Optional[str] = None,
            ip_address: Optional[str] = None):
        """Create an audit log entry."""
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address
        )
        self.db.add(log_entry)
        self.db.commit()
    
    def get_logs(self, page: int = 1, per_page: int = 20,
                 user_id: Optional[int] = None, action: Optional[str] = None,
                 resource_type: Optional[str] = None,
                 start_date: Optional[date] = None,
                 end_date: Optional[date] = None) -> Tuple[List[AuditLog], int]:
        """Get paginated audit logs with filters."""
        query = self.db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
            
        total = query.count()
        logs = query.order_by(AuditLog.created_at.desc())\
            .offset((page - 1) * per_page).limit(per_page).all()
        return logs, total
