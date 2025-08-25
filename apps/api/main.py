"""
FastAPI application initialization and configuration.
Main entry point for the LLM workshop API.
"""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from .utils.env import get_settings, Settings
from .services.llm_client import LLMClient
from .routers import inference
from .schemas.response import HealthResponse

import openlit

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global variables
app_state = {
    "llm_client": None,
    "settings": None,
    "system_prompt": None,
    "is_healthy": False
}

openlit.init(capture_message_content=True)


def load_system_prompt() -> str:
    """Load system prompt from config file."""
    config_path = Path(__file__).parent / "config" / "system_prompt.txt"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            prompt = f.read().strip()
        logger.info(f"Loaded system prompt from {config_path}")
        return prompt
    except FileNotFoundError:
        logger.warning(
            f"System prompt file not found at {config_path}, using default")
        return "You are a helpful AI assistant. Provide clear and accurate responses."
    except Exception as e:
        logger.error(f"Error loading system prompt: {e}")
        return "You are a helpful AI assistant. Provide clear and accurate responses."


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown tasks."""
    # Startup
    logger.info("Starting LLM Workshop API...")

    try:
        # Load configuration
        app_state["settings"] = get_settings()

        # Load system prompt
        app_state["system_prompt"] = load_system_prompt()

        # Initialize LLM client
        try:
            app_state["llm_client"] = LLMClient(
                app_state["settings"],
                app_state["system_prompt"]
            )

            # Test the connection
            provider_info = app_state["llm_client"].get_provider_info()
            logger.info(
                f"✅ LLM client initialized: {provider_info['provider']} provider using model {provider_info['model']}")
            app_state["is_healthy"] = True

        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM client: {e}")
            logger.warning(
                "API will start in degraded mode - chat endpoints will return 503")
            app_state["llm_client"] = None
            app_state["is_healthy"] = False

        # Store state in app for access in routes
        app.state.app_state = app_state

    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down LLM Workshop API...")


# Create FastAPI application
app = FastAPI(
    title="LLM Observability Workshop API",
    description="""
    A minimal FastAPI application for workshop demonstrations of LLM integration.
    
    This API provides a simple chat interface that works with both:
    - **Ollama** (local models like phi4-mini)
    - **Azure OpenAI** (cloud models like GPT-4)
    
    ## Features
    - Session-based conversation history
    - Environment-based provider switching
    - Ready for observability tooling
    
    ## Configuration
    Set the `LLM_PROVIDER` environment variable to either `ollama` or `azure`.
    See the `/healthz` endpoint for current configuration.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware for workshop browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Workshop-friendly (not for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with proper prefix
app.include_router(
    inference.router,
    prefix="/v1",
    tags=["chat"]
)


@app.get("/", summary="Root endpoint", description="Basic API information")
async def root():
    """Root endpoint providing basic API information."""
    return {
        "message": "LLM Workshop API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/healthz"
    }


@app.get(
    "/healthz",
    response_model=HealthResponse,
    summary="Health check",
    description="Check API health and current configuration"
)
async def health_check():
    """
    Health check endpoint providing system status and configuration info.
    Returns:
        HealthResponse with status, provider, and model information
    """
    settings = app_state["settings"]
    if not settings:
        raise HTTPException(status_code=503, detail="Service not configured")

    # Build response based on health status
    health_data = {
        "status": "healthy" if app_state["is_healthy"] else "degraded",
        "provider": getattr(settings, "llm_provider", getattr(settings, "LLM_PROVIDER", "unknown")),
        "model": getattr(settings, "ollama_model", getattr(settings, "OLLAMA_MODEL", None)) if getattr(settings, "llm_provider", getattr(settings, "LLM_PROVIDER", "ollama")) == "ollama" else getattr(settings, "azure_openai_model", getattr(settings, "AZURE_OPENAI_MODEL", None)),
    }
    # Add details if degraded
    if not app_state["is_healthy"]:
        health_data["details"] = "LLM service not available"
    return HealthResponse(**health_data)


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors with helpful message."""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Not Found",
            "available_endpoints": [
                "/",
                "/healthz",
                "/v1/chat",
                "/docs"
            ]
        }
    )
