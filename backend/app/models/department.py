from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database.session import Base

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
