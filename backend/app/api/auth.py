from fastapi import APIRouter, HTTPException, status, Body
from pydantic import BaseModel, EmailStr
from app.core.auth import create_access_token, create_refresh_token, verify_token
from app.core.config import settings
import logging

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: EmailStr

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

@router.post(
    "/login",
    response_model=TokenPair,
    responses={429: {"description": "Too Many Requests"}},
)
def login(request: LoginRequest):
    # In production, send a magic link via SES. Here, mock by logging.
    logging.info(f"[MOCK SES] Would send magic link to: {request.email}")
    # For demo, issue tokens directly
    access = create_access_token(subject=request.email)
    refresh = create_refresh_token(subject=request.email)
    return TokenPair(access_token=access, refresh_token=refresh)

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post(
    "/refresh",
    response_model=TokenPair,
    responses={401: {"description": "Unauthorized"}, 429: {"description": "Too Many Requests"}},
)
def refresh(request: RefreshRequest):
    data = verify_token(request.refresh_token, token_type="refresh")
    access = create_access_token(subject=data.sub)
    refresh = create_refresh_token(subject=data.sub)
    return TokenPair(access_token=access, refresh_token=refresh) 