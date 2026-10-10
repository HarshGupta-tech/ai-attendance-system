from pydantic import BaseModel, ConfigDict
from datetime import datetime

class AuditLogResponse(BaseModel):
    id: int
    user_id: int | None = None
    user_name: str | None = None
    action: str
    resource_type: str | None = None
    resource_id: str | None = None
    details: str | None = None
    ip_address: str | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AuditLogListResponse(BaseModel):
    logs: list[AuditLogResponse]
    total: int
    page: int
    per_page: int
