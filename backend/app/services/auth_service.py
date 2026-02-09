"""
Authentication service - integrates with Supabase Auth.
Handles OTP sending, verification, and token validation.
"""
import httpx
from typing import Dict, Any, Optional
from app.config import settings


class SupabaseAuthService:
    """Service for Supabase authentication operations."""

    def __init__(self):
        self.supabase_url = settings.supabase_url
        self.anon_key = settings.supabase_anon_key
        self.service_key = settings.supabase_service_key
        self.auth_url = f"{self.supabase_url}/auth/v1"

    def _get_headers(self, use_service_key: bool = False) -> Dict[str, str]:
        """Get headers for Supabase API requests."""
        key = self.service_key if use_service_key else self.anon_key
        return {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

    async def send_otp(self, email: str) -> Dict[str, Any]:
        """
        Send OTP to user's email via Supabase.

        Args:
            email: User's email address

        Returns:
            Response from Supabase
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auth_url}/otp",
                headers=self._get_headers(),
                json={
                    "email": email,
                    "create_user": True,  # Create user if doesn't exist
                    "options": {
                        "should_create_user": True,
                        "email_redirect_to": None  # Disable magic link, force OTP
                    }
                }
            )
            response.raise_for_status()
            return response.json()

    async def verify_otp(self, email: str, otp: str) -> Dict[str, Any]:
        """
        Verify OTP and get access token.

        Args:
            email: User's email address
            otp: One-time password code

        Returns:
            Dict with access_token, refresh_token, and user info
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auth_url}/verify",
                headers=self._get_headers(),
                json={
                    "email": email,
                    "token": otp,
                    "type": "email"
                }
            )
            response.raise_for_status()
            return response.json()

    async def get_user_from_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Validate access token and get user info.

        Args:
            access_token: JWT access token

        Returns:
            User info if token is valid, None otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.auth_url}/user",
                    headers={
                        "apikey": self.anon_key,
                        "Authorization": f"Bearer {access_token}",
                    }
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except httpx.HTTPError:
            return None

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            New access_token and refresh_token
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auth_url}/token?grant_type=refresh_token",
                headers=self._get_headers(),
                json={"refresh_token": refresh_token}
            )
            response.raise_for_status()
            return response.json()


# Global service instance
auth_service = SupabaseAuthService()
