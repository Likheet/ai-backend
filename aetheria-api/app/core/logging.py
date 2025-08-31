"""Structured logging configuration for Aetheria API."""

import json
import logging
import sys
import time
import uuid
from typing import Any, Dict, Optional

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings

settings = get_settings()


def configure_logging() -> None:
    """Configure structured logging with JSON output."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if settings.app_env == "dev" else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=False,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses."""
    
    def __init__(self, app: Any, logger: Optional[structlog.BoundLogger] = None):
        super().__init__(app)
        self.logger = logger or get_logger("api")
    
    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Log request and response details."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Add request ID to context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        
        # Add request ID to request state for access in routes
        request.state.request_id = request_id
        
        start_time = time.time()
        
        # Log incoming request
        self.logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params) if request.query_params else None,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_id=request_id,
        )
        
        try:
            response = await call_next(request)
        except Exception as exc:
            # Log exception
            self.logger.error(
                "Request failed",
                method=request.method,
                path=request.url.path,
                error=str(exc),
                error_type=type(exc).__name__,
                request_id=request_id,
            )
            raise
        
        # Calculate latency
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        # Log response
        self.logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            latency_ms=latency_ms,
            request_id=request_id,
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to each request."""
    
    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Add request ID to request state."""
        if not hasattr(request.state, "request_id"):
            request.state.request_id = str(uuid.uuid4())
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response


# Initialize logging
configure_logging()
