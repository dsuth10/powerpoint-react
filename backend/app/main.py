from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.slides import router as slides_router
from app.api.health import router as health_router
from app.core.errors import add_error_handlers
from app.core.rate_limit import rate_limit_dependency
from app.core.logging import setup_logging, set_request_id
from app.core.metrics import setup_metrics
from fastapi.openapi.utils import get_openapi
from app.core.auth import api_key_dependency
from app.core.config import settings
import os

app = FastAPI(
    title="AI PowerPoint Generator API",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    openapi_version="3.0.3",
)

# Set up CORS from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(slides_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
os.makedirs(settings.STATIC_DIR, exist_ok=True)
app.mount(settings.STATIC_URL_PATH, StaticFiles(directory=settings.STATIC_DIR), name="static")

add_error_handlers(app)

# Patch routers to add API key and rate limit to public POST routes using proper Depends
for router in [auth_router, chat_router, slides_router]:
    for route in router.routes:
        if getattr(route, "methods", None) and "POST" in route.methods:
            existing = getattr(route, "dependencies", []) or []
            deps = [Depends(rate_limit_dependency)]
            # Apply API key requirement except for auth routes
            if router not in [auth_router]:
                deps.insert(0, Depends(api_key_dependency))
            route.dependencies = [*existing, *deps]

setup_logging()
setup_metrics(app)


@app.get("/")
def read_root():
    return {"message": "AI PowerPoint Generator API"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        description="API for AI PowerPoint Generator",
    )
    # Force OpenAPI 3.0.x for compatibility with schemathesis in tests
    openapi_schema["openapi"] = "3.0.3"
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore[assignment]


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID")
    set_request_id(request_id)
    try:
        response = await call_next(request)
    finally:
        set_request_id(None)
    return response
