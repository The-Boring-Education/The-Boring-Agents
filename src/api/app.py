"""
FastAPI application for The Boring Agents API.

This is the main API application that handles all requests from the Admin UI.
All operations are logged comprehensively for monitoring and debugging.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import quiz_router, interview_prep_router, session_router
from src.api.middleware import RequestLoggingMiddleware
from src.api.logging_config import setup_api_logging
from src.core.env import get_env_manager


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    # Set up logging first
    setup_api_logging()
    
    # Get environment
    env_manager = get_env_manager()
    environment = env_manager.get("ENVIRONMENT", "dev")
    
    # Create FastAPI app
    app = FastAPI(
        title="The Boring Agents API",
        version="0.1.0",
        description="AI-powered content generation API for The Boring Education platform"
    )
    
    # Add CORS middleware for admin UI and local testing
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # Add request logging middleware
    app.add_middleware(
        RequestLoggingMiddleware,
        environment=environment
    )
    
    # Include routers
    app.include_router(quiz_router, prefix="/api/v1")
    app.include_router(interview_prep_router, prefix="/api/v1")
    app.include_router(session_router, prefix="/api/v1")
    
    # Health check endpoint
    @app.get("/api/v1/health")
    def health():
        """Health check endpoint for monitoring."""
        return {
            "ok": True,
            "service": "The Boring Agents API",
            "version": app.version,
            "environment": environment
        }
    
    return app


app = create_app()
