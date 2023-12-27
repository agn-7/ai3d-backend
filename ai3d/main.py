from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .endpoints import router


def create_app() -> FastAPI:
    """
    Returns a FastAPI app object.
    """
    app = FastAPI(title="ai3d", openapi_url="/api/openapi.json", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

    app.include_router(router, prefix="/api")
    return app


app = create_app()
