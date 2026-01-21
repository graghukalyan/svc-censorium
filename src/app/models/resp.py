"""Response models."""
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Base response model."""
    success: bool = Field(True, description="Operation success status")


class ItemResponse(BaseResponse):
    """Response model for item data."""
    
    id: int
    name: str
    description: str | None = None
    
    class Config:
        from_attributes = True
