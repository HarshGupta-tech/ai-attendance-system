from sqlalchemy.orm import Session
from app.models import SystemSetting
from typing import List, Optional

class SettingsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[SystemSetting]:
        return self.db.query(SystemSetting).all()
    
    def get(self, key: str) -> Optional[str]:
        setting = self.db.query(SystemSetting).filter(SystemSetting.key == key).first()
        return setting.value if setting else None
    
    def set(self, key: str, value: str, description: Optional[str] = None,
            updated_by: Optional[int] = None) -> SystemSetting:
        """Create or update a setting."""
        setting = self.db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if setting:
            setting.value = value
            if description:
                setting.description = description
            if updated_by:
                setting.updated_by = updated_by
        else:
            setting = SystemSetting(
                key=key, 
                value=value, 
                description=description,
                updated_by=updated_by
            )
            self.db.add(setting)
            
        self.db.commit()
        self.db.refresh(setting)
        return setting
    
    def delete(self, key: str) -> bool:
        deleted = self.db.query(SystemSetting).filter(SystemSetting.key == key).delete()
        self.db.commit()
        return deleted > 0
    
    def initialize_defaults(self):
        """Initialize default system settings if they don't exist."""
        defaults = {
            'face_recognition_threshold': ('0.6', 'Face recognition distance threshold'),
            'low_attendance_threshold': ('75.0', 'Percentage below which attendance is considered low'),
            'late_threshold_minutes': ('15', 'Minutes after session start to mark as late'),
            'max_face_samples': ('10', 'Maximum face samples per student'),
            'enable_liveness': ('true', 'Enable liveness detection during attendance'),
            'enable_notifications': ('true', 'Enable notification system'),
            'smtp_configured': ('false', 'Whether SMTP email is configured'),
            'system_name': ('AI Attendance System', 'System display name'),
        }
        for key, (value, desc) in defaults.items():
            existing = self.db.query(SystemSetting).filter(SystemSetting.key == key).first()
            if not existing:
                self.set(key, value, desc)
