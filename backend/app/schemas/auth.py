"""
Authentication schemas - Pydantic models for auth requests/responses.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class SendOTPRequest(BaseModel):
    """Request to send OTP to email."""
    email: EmailStr


class SendOTPResponse(BaseModel):
    """Response after sending OTP."""
    message: str = "OTP sent to your email"


class VerifyOTPRequest(BaseModel):
    """Request to verify OTP."""
    email: EmailStr
    otp: str


class UserResponse(BaseModel):
    """User information response."""
    id: UUID
    email: str
    created_at: datetime
    last_entry_date: Optional[datetime] = None


class TokenResponse(BaseModel):
    """Response with access token and user info."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Request to refresh access token."""
    refresh_token: str
