from fastapi import FastAPI

from app.api.router import api_router
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
        # Keep local bootstrap simple; production should rely on Alembic migrations.
        Base.metadata.create_all(bind=engine)

    return app


app = create_app()
