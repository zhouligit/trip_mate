from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.database import Base, engine
from app import models  # noqa: F401


def create_app() -> FastAPI:
    app = FastAPI(
        title="TripMate Backend",
        description="TripMate MVP backend service based on FastAPI",
        version="0.1.0",
    )
    app.include_router(api_router, prefix="/api")

    @app.on_event("startup")
    def on_startup() -> None:
        # Production/staging: schema comes from Alembic only.
        # Dev/local: optional bootstrap for empty DB without running migrations.
        env = settings.app_env.lower()
        if env in ("dev", "development", "local"):
            Base.metadata.create_all(bind=engine)

    return app


app = create_app()
