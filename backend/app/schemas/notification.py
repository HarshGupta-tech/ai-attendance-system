from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class NotificationCreate(BaseModel):
    user_id: int
    title: str = Field(max_length=200)
    message: str
    type: str = "info"

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
