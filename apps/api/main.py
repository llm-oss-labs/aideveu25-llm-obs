"""
FastAPI application initialization and configuration.
Main entry point for the LLM workshop API.
"""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .utils.env import get_settings, validate_provider_config, Settings
from .services.llm_client import LLMClient
from .routers import inference
from .schemas.response import HealthResponse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global variables for dependency injection
_llm_client: LLMClient = None
_settings: Settings = None
_system_prompt: str = None


def load_system_prompt() -> str:
    """Load system prompt from config file."""
    config_path = Path(__file__).parent / "config" / "system_prompt.txt"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            prompt = f.read().strip()
        logger.info(f"Loaded system prompt from {config_path}")
        return prompt
    except FileNotFoundError:
        logger.warning(f"System prompt file not found at {config_path}, using default")
        return "You are a helpful AI assistant. Provide clear and accurate responses."
    except Exception as e:
        logger.error(f"Error loading system prompt: {e}")
        return "You are a helpful AI assistant. Provide clear and accurate responses."


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown tasks."""
    global _llm_client, _settings, _system_prompt
    
    # Startup
    logger.info("Starting LLM Workshop API...")
    
    try:
        # Load configuration
        _settings = get_settings()
        validate_provider_config(_settings)
        
        # Load system prompt
        _system_prompt = load_system_prompt()
        
        # Initialize LLM client
        _llm_client = LLMClient(_settings, _system_prompt)
        
        # Setup router dependency injection
        from .routers.inference import set_llm_client
        set_llm_client(_llm_client)
        
        # Log startup info
        provider_info = _llm_client.get_provider_info()
        logger.info(f"API started successfully with {provider_info['provider']} provider using model {provider_info['model']}")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down LLM Workshop API...")


# Dependency injection functions
def get_llm_client() -> LLMClient:
    """Dependency injection for LLM client."""
    if _llm_client is None:
        raise HTTPException(status_code=500, detail="LLM client not initialized")
    return _llm_client


def get_app_settings() -> Settings:
    """Dependency injection for app settings."""
    if _settings is None:
        raise HTTPException(status_code=500, detail="Application settings not initialized")
    return _settings


# Create FastAPI application
app = FastAPI(
    title="LLM Workshop API",
    description="""
    A minimal FastAPI application for workshop demonstrations of LLM integration.
    
    This API provides a simple chat interface that works with both:
    - **Ollama** (local models like Phi3)
    - **Azure OpenAI** (cloud models like GPT-4)
    
    ## Features
    - Session-based conversation history
    - Environment-based provider switching
    - Minimal LangChain integration
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

# Include routers
app.include_router(inference.router)


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
async def health_check(
    settings: Settings = Depends(get_app_settings),
    llm_client: LLMClient = Depends(get_llm_client)
):
    """
    Health check endpoint providing system status and configuration info.
    
    Returns:
        HealthResponse with status, provider, and model information
    """
    try:
        provider_info = llm_client.get_provider_info()
        
        return HealthResponse(
            status="healthy",
            provider=provider_info["provider"],
            model=provider_info["model"]
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="Service unavailable"
        )


