"""
Response schemas for the LLM Workshop API.
"""
from typing import Optional
from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    session_id: str = Field(..., description="Session identifier")
    reply: str = Field(..., description="LLM-generated response")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "user-123-session-456",
                "reply": "I'd be happy to help you with that! Python is a versatile programming language..."
            }
        }
    }


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""
    status: str = Field(..., description="Service health status", pattern="^(healthy|degraded|unhealthy)$")
    provider: str = Field(..., description="LLM provider (ollama or azure)")
    model: str = Field(..., description="Model being used")
    details: Optional[str] = Field(None, description="Additional details if service is degraded")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "provider": "ollama",
                "model": "phi3"
            }
        }
    }
    