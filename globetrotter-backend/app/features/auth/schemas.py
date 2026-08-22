from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SignupRequest(BaseModel):
    # NOTE: photo_url is optional at registration. The primary path for profile photo upload
    # is signing up first, then calling POST /api/auth/me/photo separately.
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str
    last_name: str
    phone_number: str | None = None
    city: str | None = None
    country: str | None = None
    additional_info: str | None = None
    photo_url: str | None = None


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    city: str | None = None
    country: str | None = None
    additional_info: str | None = None
    language: str | None = None


class LoginRequest(BaseModel):
    # NOTE: Accepts either an email address or a phone number.
    # The frontend should label this input field "Email or Phone" instead of "Username".
    email: str = Field(..., description="Email address or phone number")
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: str | None = None
    city: str | None = None
    country: str | None = None
    additional_info: str | None = None
    photo_url: str | None = None
    language: str
    is_admin: bool
    created_at: datetime


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
