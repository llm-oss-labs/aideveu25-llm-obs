"""
Chat inference router for handling LLM chat requests.
Provides endpoints for chat interactions and session management.
"""
import logging
import time
from fastapi import APIRouter, HTTPException
from typing import Dict

from ..schemas.request import ChatRequest
from ..schemas.response import ChatResponse, ErrorResponse

# Configure logging
logger = logging.getLogger(__name__)

# Router instance
router = APIRouter(prefix="/v1", tags=["inference"])

# Global LLM client - will be set by main.py
_llm_client = None

def set_llm_client(client):
    """Set the global LLM client instance."""
    global _llm_client
    _llm_client = client


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Process chat message",
    description="""
    Send a message to the AI assistant and receive a response.
    
    The API maintains conversation history per session_id, so you can have
    multi-turn conversations by using the same session_id across requests.
    
    **Request Body:**
    - `session_id`: Unique identifier for your conversation (1-100 characters)
    - `user_message`: Your message to the AI (1-10,000 characters)
    
    **Response:**
    - `session_id`: Your session ID (echoed back)
    - `reply`: The AI assistant's response
    
    **Session Management:**
    - Sessions are stored in memory and persist across requests
    - Sessions are automatically cleaned up to prevent memory bloat
    - No authentication required (workshop environment)
    """
)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message and return AI response.
    
    This endpoint:
    1. Validates the incoming request
    2. Retrieves conversation history for the session
    3. Sends the complete context to the LLM
    4. Returns the AI's response
    5. Updates the session history
    
    Args:
        request: Chat request containing session_id and user_message
        
    Returns:
        ChatResponse with session_id and AI reply
        
    Raises:
        HTTPException: If request validation fails or LLM call errors
    """
    if _llm_client is None:
        raise HTTPException(status_code=500, detail="LLM client not initialized")
    
    start_time = time.time()
    
    try:
        logger.info(f"Received chat request for session: {request.session_id}")
        
        # Validate input length (additional server-side validation)
        if len(request.user_message.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="User message cannot be empty"
            )
        
        # Process the chat request
        ai_reply = await _llm_client.chat(
            session_id=request.session_id,
            user_message=request.user_message
        )
        
        # Log successful completion
        duration = time.time() - start_time
        logger.info(f"Chat completed for session {request.session_id} in {duration:.2f}s")
        
        return ChatResponse(
            session_id=request.session_id,
            reply=ai_reply
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (client errors)
        raise
    except Exception as e:
        # Log server errors and return 500
        duration = time.time() - start_time
        logger.error(f"Chat failed for session {request.session_id} after {duration:.2f}s: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: Failed to process chat request"
        )
