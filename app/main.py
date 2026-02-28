"""Pasanaku API - Entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import auth as auth_router
from app.core.config import settings
from app.shared.database import create_db_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    await create_db_tables()
    yield


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(
        auth_router.router,
        prefix=f"{settings.API_V1_STR}/auth",
        tags=["auth"],
    )

    @application.get("/health", tags=["health"])
    async def health_check() -> dict:
        return {"status": "ok", "version": settings.VERSION}

    return application


app = create_application()
