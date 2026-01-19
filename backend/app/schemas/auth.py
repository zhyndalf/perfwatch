"""Authentication-related Pydantic schemas."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Request body for login endpoint."""

    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Response body for successful login."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds until expiration


class PasswordChangeRequest(BaseModel):
    """Request body for password change endpoint."""

    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=128)
