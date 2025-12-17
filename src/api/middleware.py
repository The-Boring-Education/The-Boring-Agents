"""
Request/Response logging middleware for The Boring Agents API.

Provides comprehensive logging of all API requests and responses
with request ID tracking, timing, and structured JSON logging.
"""

import time
import uuid
import json
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all API requests and responses.
    
    Features:
    - Request ID generation for traceability
    - Request/response logging with timing
    - Structured JSON logging
    - Sensitive data masking
    - Environment context
    """
    
    # Paths to exclude from detailed logging
    EXCLUDED_PATHS = ["/health", "/docs", "/openapi.json", "/redoc"]
    
    # Fields to mask in logs (sensitive data)
    SENSITIVE_FIELDS = [
        "api_key", "apiKey", "api-key",
        "secret", "password", "token",
        "authorization", "auth",
        "openai_api_key", "anthropic_api_key", "huggingface_api_key"
    ]
    
    def __init__(self, app: ASGIApp, environment: str = "dev"):
        """
        Initialize the middleware.
        
        Args:
            app: The ASGI application
            environment: Environment name (local, dev, prod)
        """
        super().__init__(app)
        self.environment = environment
    
    def _mask_sensitive_data(self, data: dict) -> dict:
        """
        Mask sensitive fields in request/response data.
        
        Args:
            data: Dictionary to mask
            
        Returns:
            Dictionary with sensitive values masked
        """
        if not isinstance(data, dict):
            return data
        
        masked = {}
        for key, value in data.items():
            key_lower = key.lower()
            # Check if this field should be masked
            if any(sensitive in key_lower for sensitive in self.SENSITIVE_FIELDS):
                masked[key] = "***"
            elif isinstance(value, dict):
                masked[key] = self._mask_sensitive_data(value)
            elif isinstance(value, list):
                masked[key] = [
                    self._mask_sensitive_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                masked[key] = value
        
        return masked
    
    def _should_log_details(self, path: str) -> bool:
        """
        Check if detailed logging should be performed for this path.
        
        Args:
            path: Request path
            
        Returns:
            True if detailed logging should be performed
        """
        return not any(path.startswith(excluded) for excluded in self.EXCLUDED_PATHS)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and log details.
        
        Args:
            request: The incoming request
            call_next: The next middleware/handler
            
        Returns:
            The response
        """
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Get request details
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        
        # Get request body if available
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    # Re-create request body for downstream handlers
                    async def receive():
                        return {"type": "http.request", "body": body_bytes}
                    request._receive = receive
                    
                    try:
                        body = json.loads(body_bytes.decode())
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        body = {"raw": "non-json body"}
            except Exception:
                body = None
        
        # Log request
        if self._should_log_details(path):
            log_data = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "level": "INFO",
                "type": "request",
                "request_id": request_id,
                "method": method,
                "path": path,
                "environment": self.environment,
                "query_params": self._mask_sensitive_data(query_params) if query_params else None,
            }
            
            if body:
                log_data["body"] = self._mask_sensitive_data(body)
            
            logger.info(f"API Request: {json.dumps(log_data)}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Get response status
            status_code = response.status_code
            
            # Log response
            if self._should_log_details(path):
                log_data = {
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "level": "INFO" if status_code < 400 else "ERROR",
                    "type": "response",
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                    "environment": self.environment,
                }
                
                logger.info(f"API Response: {json.dumps(log_data)}")
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Log error
            duration_ms = int((time.time() - start_time) * 1000)
            
            log_data = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "level": "ERROR",
                "type": "error",
                "request_id": request_id,
                "method": method,
                "path": path,
                "duration_ms": duration_ms,
                "environment": self.environment,
                "error": str(e),
                "error_type": type(e).__name__,
            }
            
            logger.error(f"API Error: {json.dumps(log_data)}", exc_info=True)
            
            # Re-raise the exception
            raise

