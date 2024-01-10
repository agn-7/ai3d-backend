from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin

from .endpoints import router
from .database import engine
from .admins import UserAdmin, InteractionAdmin, AdminAuth
from .auth import SECRET_KEY


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

authentication_backend = AdminAuth(secret_key=SECRET_KEY)
admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)
admin.add_view(UserAdmin)
admin.add_view(InteractionAdmin)
