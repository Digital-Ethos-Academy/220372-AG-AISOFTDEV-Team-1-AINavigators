"""
FastAPI application entry point for StaffAlloc.

This module creates and configures the main FastAPI application instance,
including middleware, exception handlers, event handlers, and router inclusions.
"""
import logging
import sys
from pathlib import Path

import httpx
import structlog
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, UJSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

# Import routers from the api package
from app.api import admin, ai, allocations, employees, projects, reports
from app.core.config import settings
from app.core.exceptions import AppException
from app.db.session import create_db_and_tables, get_db

# --- Logging Configuration (as per Architecture Document) ---

# Ensure logs are not duplicated by the root handler
logging.basicConfig(handlers=[logging.NullHandler()])

# Configure structlog for structured, JSON-formatted logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
logger = structlog.get_logger(__name__)


# --- Application Factory ---

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Local-first prototype for an AI-driven staff allocation platform.",
        version=settings.VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/v1/openapi.json",
        default_response_class=UJSONResponse,
    )

    # --- Middleware Configuration ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Event Handlers (Startup/Shutdown) ---
    @app.on_event("startup")
    async def startup_event():
        """
        Application startup logic:
        - Initializes logging.
        - Ensures necessary data directories exist for the local-first setup.
        """
        logger.info("Starting up StaffAlloc API...")
        # Ensure data directories exist as per the architecture document
        Path(settings.SQLITE_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        Path(settings.VECTOR_STORE_PATH).mkdir(parents=True, exist_ok=True)
        Path(settings.REPORTS_PATH).mkdir(parents=True, exist_ok=True)
        create_db_and_tables()
        logger.info(
            "Data directories ensured",
            db=str(Path(settings.SQLITE_DB_PATH).parent),
            vector_store=settings.VECTOR_STORE_PATH,
            reports=settings.REPORTS_PATH,
        )
        logger.info("Application startup complete.")

    @app.on_event("shutdown")
    async def shutdown_event():
        """Application shutdown logic."""
        logger.info("Shutting down StaffAlloc API...")

    # --- Exception Handlers ---
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """Handles custom application-specific exceptions."""
        logger.warning(
            "Application exception caught",
            status_code=exc.status_code,
            detail=exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handles FastAPI request validation errors for cleaner responses."""
        logger.warning("Request validation error", url=str(request.url), errors=exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handles any other unhandled exceptions, preventing crashes."""
        logger.error("Unhandled exception", exc_info=sys.exc_info(), url=str(request.url))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected internal server error occurred."},
        )

    # --- API Router Inclusions ---
    api_v1_prefix = settings.API_V1_STR
    app.include_router(projects.router, prefix=api_v1_prefix, tags=["Projects"])
    app.include_router(allocations.router, prefix=api_v1_prefix, tags=["Allocations"])
    app.include_router(employees.router, prefix=api_v1_prefix, tags=["Employees"])
    app.include_router(admin.router, prefix=api_v1_prefix, tags=["Admin (Roles/LCATs)"])
    app.include_router(reports.router, prefix=api_v1_prefix, tags=["Reports"])
    app.include_router(ai.router, prefix=api_v1_prefix, tags=["AI"])

    return app


app = create_app()


# --- Root and Health Check Endpoints ---

@app.get("/", include_in_schema=False)
def read_root():
    """Provides basic information about the API and links to the documentation."""
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "docs_url": app.docs_url,
        "redoc_url": app.redoc_url,
    }


@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """
    Performs a health check of the API and its critical dependencies.
    Checks for database connectivity and local LLM service availability.
    """
    db_status = "ok"
    llm_status = "ok"

    # 1. Check database connection
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        db_status = "error"

    # 2. Check local LLM service (Ollama)
    try:
        import httpx
        with httpx.Client(timeout=5.0) as client:
            # Ollama's root endpoint returns "Ollama is running"
            response = client.get(settings.OLLAMA_API_URL)
            response.raise_for_status()
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logger.warning("LLM service health check failed", error=str(e))
        llm_status = "unavailable"  # Changed to warning level since AI is optional for MVP

    if db_status == "ok":
        return {
            "status": "healthy",
            "dependencies": {
                "database": db_status,
                "llm_service": llm_status
            }
        }

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "status": "unhealthy",
            "dependencies": {"database": db_status, "llm_service": llm_status},
        },
    )
