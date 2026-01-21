"""Request models."""
from pydantic import BaseModel, Field


class BaseRequest(BaseModel):
    """Base request model."""
    pass


class CreateItemRequest(BaseRequest):
    """Request model for creating an item."""
    
    name: str = Field(..., description="Item name")
    description: str | None = Field(None, description="Item description")
