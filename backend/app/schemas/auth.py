"""Authentication request and response schemas."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class AuthRequest(BaseModel):
    """Credentials accepted by registration and login endpoints."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def enforce_bcrypt_byte_limit(cls, password: str) -> str:
        """Reject multi-byte passwords that exceed bcrypt's 72-byte input limit."""
        if len(password.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 UTF-8 bytes for bcrypt.")
        return password


class UserResponse(BaseModel):
    """Public account fields returned to clients."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr


class TokenResponse(BaseModel):
    """Bearer token response compatible with OAuth2 clients."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse