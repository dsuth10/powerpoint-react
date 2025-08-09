from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])

class HealthResponse(BaseModel):
    status: str
    version: str
    git_sha: str

@router.get("/health", response_model=HealthResponse)
def health():
    # In production, fetch real build metadata and git SHA
    return HealthResponse(status="ok", version="1.0.0", git_sha="mock-sha") 