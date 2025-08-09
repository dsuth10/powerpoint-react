from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.slides import router as slides_router
from app.api.health import router as health_router
from app.socketio_app import ws_app as socketio_ws_app
from app.core.errors import add_error_handlers
from app.core.rate_limit import rate_limit_dependency
from app.core.logging import setup_logging
from app.core.metrics import setup_metrics

app = FastAPI(
    title="AI PowerPoint Generator API",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(slides_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
app.mount("/ws", socketio_ws_app)

add_error_handlers(app)

# Patch routers to add rate limit to public POST routes using proper Depends
for router in [auth_router, chat_router, slides_router]:
    for route in router.routes:
        if getattr(route, "methods", None) and "POST" in route.methods:
            existing = getattr(route, "dependencies", []) or []
            route.dependencies = [*existing, Depends(rate_limit_dependency)]

setup_logging()
setup_metrics(app)


@app.get("/")
def read_root():
    return {"message": "AI PowerPoint Generator API"}
