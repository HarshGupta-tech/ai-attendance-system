from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SystemSettingResponse(BaseModel):
    id: int
    key: str
    value: str | None = None
    description: str | None = None
    updated_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)

class SystemSettingUpdate(BaseModel):
    value: str
