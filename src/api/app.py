from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .quiz_routes import router as quiz_router
from .interview_routes import router as interview_router


def create_app() -> FastAPI:
    app = FastAPI(title="The Boring Agents API", version="0.1.0")

    # CORS for admin UI and local testing
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    app.include_router(quiz_router, prefix="/api/v1")
    app.include_router(interview_router, prefix="/api/v1")

    @app.get("/health")
    def health():
        return {"ok": True}

    return app


app = create_app()

