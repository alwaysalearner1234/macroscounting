"""Password hashing and stateless JWT helpers."""

from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import settings

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password with bcrypt, rejecting values beyond bcrypt's byte limit."""
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password must be at most 72 UTF-8 bytes for bcrypt.")
    return password_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Compare a plaintext password to its salted bcrypt hash."""
    if len(password.encode("utf-8")) > 72:
        return False
    return password_context.verify(password, hashed_password)


def create_access_token(subject: str) -> str:
    """Create a signed access token containing a subject and expiration."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_access_token(token: str) -> str | None:
    """Return the token subject when the signature and expiry are valid."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp"]},
        )
    except jwt.PyJWTError:
        return None
    subject = payload.get("sub")
    return subject if isinstance(subject, str) else None