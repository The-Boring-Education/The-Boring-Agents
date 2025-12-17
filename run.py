"""
API server entry point for The Boring Agents.

This module starts the FastAPI server using environment variables
for configuration.
"""
import uvicorn
import logging

# Import environment manager early to ensure env vars are loaded
from src.core.env import get_env_manager, get_env_int

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Start the FastAPI server."""
    # Get environment manager to ensure env vars are loaded
    env_manager = get_env_manager()
    
    # Get server configuration from environment
    host = get_env_manager().get("AGENTS_API_HOST", "0.0.0.0")
    port = get_env_manager().get_int("AGENTS_API_PORT", 8088)
    reload = get_env_manager().get_bool("RELOAD", True)
    
    logger.info(f"Starting The Boring Agents API server on {host}:{port}")
    logger.info(f"Reload mode: {reload}")
    
    # Start the server
    uvicorn.run(
        "src.api.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
