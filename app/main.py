"""FastAPI application factory and configuration."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, users, products, shops, carts, payment, support
from app.core.config import get_settings
from app.core.db import engine, Base

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Creates database tables on startup.
    """
    # Startup: Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: Cleanup if needed
    await engine.dispose()


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="TechHouse E-Commerce Backend API",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(
        auth.router,
        prefix=settings.api_prefix,
    )
    app.include_router(
        users.router,
        prefix=settings.api_prefix,
    )
    app.include_router(
        products.router,
        prefix=settings.api_prefix,
    )
    app.include_router(
        shops.router,
        prefix=settings.api_prefix,
    )
    app.include_router(
        carts.router,
        prefix=settings.api_prefix,
    )
    app.include_router(
        payment.router,
        prefix=settings.api_prefix,
    )
    app.include_router(
        support.router,
        prefix=settings.api_prefix,
    )

    # Health check endpoint
    @app.get("/health")
    async def health_check() -> dict:
        """API health check endpoint."""
        return {"status": "healthy", "service": settings.app_name}

    # Root endpoint
    @app.get("/")
    async def root() -> dict:
        """Root endpoint."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "docs": "/api/docs",
        }

    return app


# Create the FastAPI app
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
