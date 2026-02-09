"""
Authentication API endpoints.
Handles OTP sending, verification, and user info retrieval.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    SendOTPRequest,
    SendOTPResponse,
    VerifyOTPRequest,
    TokenResponse,
    UserResponse
)
from app.services.auth_service import auth_service
from app.dependencies import get_current_user
import httpx

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/send-otp", response_model=SendOTPResponse)
async def send_otp(request: SendOTPRequest):
    """
    Send OTP to user's email.
    User will receive an email with a one-time password.
    """
    try:
        await auth_service.send_otp(request.email)
        return SendOTPResponse(message="OTP sent to your email")
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP: {str(e)}"
        )


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    request: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify OTP and create/login user.
    Returns access token for authenticated requests.
    """
    try:
        # Verify OTP with Supabase
        auth_response = await auth_service.verify_otp(request.email, request.otp)
        access_token = auth_response.get("access_token")
        supabase_user = auth_response.get("user")

        if not access_token or not supabase_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid OTP"
            )

        supabase_user_id = UUID(supabase_user["id"])
        email = supabase_user["email"]

        # Check if user exists in our database
        result = await db.execute(
            select(User).where(User.supabase_user_id == supabase_user_id)
        )
        user = result.scalar_one_or_none()

        # Create user if doesn't exist
        if not user:
            user = User(
                supabase_user_id=supabase_user_id,
                email=email
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        # Return token and user info
        return TokenResponse(
            access_token=access_token,
            user=UserResponse(
                id=user.id,
                email=user.email,
                created_at=user.created_at,
                last_entry_date=user.last_entry_date
            )
        )

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"OTP verification failed: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information.
    Requires valid access token in Authorization header.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at,
        last_entry_date=current_user.last_entry_date
    )
