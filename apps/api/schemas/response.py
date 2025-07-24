"""
Pydantic schemas for API response validation.
"""
from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    
    session_id: str = Field(
        ..., 
        description="Session identifier echoed from the request"
    )
    reply: str = Field(
        ..., 
        description="The AI assistant's response message"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "user-123-session-456",
                "reply": "Python decorators are a way to modify or enhance functions..."
            }
        }
    }


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""
    
    status: str = Field(
        ..., 
        description="Application health status"
    )
    provider: str = Field(
        ..., 
        description="Current LLM provider being used"
    )
    model: str = Field(
        ..., 
        description="Current model being used"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "provider": "ollama",
                "model": "phi3"
            }
        }
    }


class ErrorResponse(BaseModel):
    """Response schema for error responses."""
    
    error: str = Field(
        ..., 
        description="Error message describing what went wrong"
    )
    detail: str = Field(
        default="", 
        description="Additional error details if available"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "Invalid request",
                "detail": "session_id field is required"
            }
        }
    }
