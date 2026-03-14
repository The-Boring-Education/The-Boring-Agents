"""
FastAPI application for The Boring Agents API.

This is the main API application that handles all requests from the Admin UI.
All operations are logged comprehensively for monitoring and debugging.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.logging_config import setup_api_logging
from src.api.middleware import RequestLoggingMiddleware
from src.api.routes import (
    aptitude_router,
    interview_prep_router,
    quiz_router,
    session_router,
)
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
        description="AI-powered content generation API for The Boring Education platform",
    )

    # Add CORS middleware for admin UI and local testing
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware, environment=environment)

    # Include routers
    app.include_router(quiz_router, prefix="/api/v1")
    app.include_router(interview_prep_router, prefix="/api/v1")
    app.include_router(session_router, prefix="/api/v1")
    app.include_router(aptitude_router, prefix="/api/v1")

    # Root API endpoint
    @app.get("/api/v1")
    def api_root():
        """Root API endpoint providing documentation and available endpoints."""
        return {
            "service": "The Boring Agents API",
            "version": app.version,
            "environment": environment,
            "status": "online",
            "endpoints": {
                "health": "/api/v1/health",
                "ping": "/api/v1/ping",
                "quiz": {
                    "generate_topic": "POST /api/v1/quiz/topics",
                    "get_topics": "GET /api/v1/quiz/topics",
                    "get_session": "GET /api/v1/quiz/session/{id}",
                    "get_session_output": "GET /api/v1/quiz/session/{id}/output",
                },
                "interview": {
                    "generate_topic": "POST /api/v1/interview/generate-topic",
                    "create_sheet": "POST /api/v1/interview/sheets",
                    "get_session": "GET /api/v1/interview/session/{id}",
                    "get_session_output": "GET /api/v1/interview/session/{id}/output",
                },
                "aptitude": {
                    "generate": "POST /api/v1/aptitude/generate",
                    "generate_batch": "POST /api/v1/aptitude/generate-batch",
                    "generate_study_guide": "POST /api/v1/aptitude/generate-study-guide",
                    "upload_study_guide": "POST /api/v1/aptitude/upload-study-guide",
                    "topics": "GET /api/v1/aptitude/topics",
                    "upload": "POST /api/v1/aptitude/upload",
                },
            },
            "docs": "/docs",
        }

    # Health check endpoint
    @app.get("/api/v1/health")
    def health():
        """Health check endpoint for monitoring."""
        return {
            "ok": True,
            "service": "The Boring Agents API",
            "version": app.version,
            "environment": environment,
        }

    # Ping endpoint
    @app.get("/api/v1/ping")
    def ping():
        """Ping endpoint (alias for health check)."""
        return {
            "ok": True,
            "service": "The Boring Agents API",
            "version": app.version,
            "environment": environment,
        }

    return app


app = create_app()
