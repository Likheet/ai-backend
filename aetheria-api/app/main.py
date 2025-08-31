"""Main FastAPI application for Aetheria Salon AI Backend."""

import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings
from app.core.logging import LoggingMiddleware, RequestIdMiddleware, get_logger
from app.core.db import create_db_pool, close_db_pool

# Import routers
from app.routers import health, intake, machine, engine, compare

# Initialize settings and logger
settings = get_settings()
logger = get_logger(__name__)


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """Simple API key authentication middleware."""
    
    def __init__(self, app, api_key: str):
        super().__init__(app)
        self.api_key = api_key
    
    async def dispatch(self, request: Request, call_next):
        """Check API key for production environment."""
        
        # Skip auth for health endpoint
        if request.url.path == "/healthz":
            return await call_next(request)
        
        # Skip auth in dev environment
        if not settings.is_production:
            return await call_next(request)
        
        # Check API key in production
        if not self.api_key:
            logger.warning("No API key configured in production environment")
            return await call_next(request)
        
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != self.api_key:
            logger.warning("Invalid or missing API key", 
                         client_ip=request.client.host if request.client else None)
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid or missing API key"}
            )
        
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    
    # Startup
    logger.info("Starting Aetheria API", version="0.1.0", environment=settings.app_env)
    
    try:
        # Initialize database connection pool
        await create_db_pool()
        logger.info("Database connection pool initialized")
    except Exception as e:
        logger.error("Failed to initialize database connection", error=str(e))
        # Continue startup even if DB connection fails for development
        if settings.is_production:
            raise
    
    logger.info("Aetheria API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Aetheria API")
    
    try:
        await close_db_pool()
        logger.info("Database connection pool closed")
    except Exception as e:
        logger.error("Error during database cleanup", error=str(e))
    
    logger.info("Aetheria API shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Aetheria Salon AI API",
    description="AI-powered salon management and treatment recommendation system",
    version="0.1.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan
)

# Add security headers
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"] if settings.app_env == "dev" else ["localhost", "127.0.0.1"]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"]
)

# Add custom middleware
app.add_middleware(APIKeyAuthMiddleware, api_key=settings.api_key)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIdMiddleware)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    logger.error(
        "Unhandled exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "request_id": request_id
        }
    )


# Include routers
app.include_router(health.router)
app.include_router(intake.router, prefix="/api/v1")
app.include_router(machine.router, prefix="/api/v1")
app.include_router(engine.router, prefix="/api/v1")
app.include_router(compare.router, prefix="/api/v1")


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint."""
    return {
        "message": "Aetheria Salon AI API",
        "version": "0.1.0",
        "docs": "/docs" if not settings.is_production else "Documentation disabled in production"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_env == "dev",
        log_config=None  # Use our custom logging configuration
    )
