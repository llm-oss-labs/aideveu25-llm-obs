"""
Chat inference router for handling LLM interactions.
"""
import logging
from typing import Dict, List
from fastapi import APIRouter, HTTPException, Request
from apps.api.schemas.request import ChatRequest
from apps.api.schemas.response import ChatResponse
from apps.api.utils.pii_masker import PIIMasker

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory session storage
sessions: Dict[str, List[Dict[str, str]]] = {}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, app_request: Request):
    """
    Process chat requests.

    Args:
        request: ChatRequest with session_id and user_message
        app_request: FastAPI Request to access app state

    Returns:
        ChatResponse with session_id and reply
    """
    # Get app state
    app_state = app_request.app.state.app_state
    llm_client = app_state.get("llm_client")
    settings = app_state.get("settings")

    # Check if LLM client is available
    if not llm_client:
        logger.error("Chat request received but LLM client is not available")
        raise HTTPException(
            status_code=503,
            detail="LLM service unavailable. Please check your configuration."
        )
    user_message = request.user_message

    try:
        pii_masking_enabled = True if settings is None else getattr(
            settings, "pii_masking_enabled", True)
        if pii_masking_enabled:
            user_message = PIIMasker.get_instance().mask(user_message)
    except Exception as e:
        logger.warning(
            f"PII masking failed, proceeding with original message: {e}")

    try:
        # Get or create session
        if request.session_id not in sessions:
            sessions[request.session_id] = []
            logger.info(f"Created new session: {request.session_id}")

        # Add user message to session
        sessions[request.session_id].append({
            "role": "user",
            "content": user_message
        })

        logger.info(f"Processing chat for session {request.session_id}")

        # Generate response using the client's chat method
        reply = await llm_client.chat(
            session_id=request.session_id,
            user_message=user_message
        )

        # Add assistant response to session
        sessions[request.session_id].append({
            "role": "assistant",
            "content": reply
        })

        # Return response
        return ChatResponse(
            session_id=request.session_id,
            reply=reply
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")

        # Parse error and provide generic helpful messages
        error_msg = str(e).lower()

        if "connection" in error_msg or "refused" in error_msg:
            detail = "Cannot connect to LLM service. Please check your configuration and ensure the service is running."
        elif "unauthorized" in error_msg or "401" in error_msg or "403" in error_msg:
            detail = "Authentication failed. Please check your API credentials."
        elif "model" in error_msg and ("not found" in error_msg or "404" in error_msg):
            detail = "Model not found. Please verify the model name in your configuration."
        elif "rate" in error_msg and "limit" in error_msg:
            detail = "Rate limit exceeded. Please try again later."
        elif "timeout" in error_msg:
            detail = "Request timed out. The service might be overloaded."
        else:
            detail = f"Failed to process chat request: {str(e)}"

        raise HTTPException(status_code=500, detail=detail)
