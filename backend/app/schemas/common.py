from pydantic import BaseModel, Field

class MessageResponse(BaseModel):
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    search: str | None = None
    sort_by: str | None = None
    sort_order: str = "asc"
