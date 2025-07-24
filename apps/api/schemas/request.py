"""
Pydantic schemas for API request validation.
"""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    
    session_id: str = Field(
        ..., 
        description="Unique identifier for the conversation session",
        min_length=1,
        max_length=100
    )
    user_message: str = Field(
        ..., 
        description="The user's message content",
        min_length=1,
        max_length=10000
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "user-123-session-456",
                "user_message": "Hello! Can you help me understand Python decorators?"
            }
        }
    }
