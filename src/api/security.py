"""Security utilities for request authentication."""

from datetime import datetime, timezone
from typing import Any, Dict

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.core.config import settings


_bearer_scheme = HTTPBearer(auto_error=True)


def _decode_jwt(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT using configured settings."""
    options = {"verify_aud": bool(settings.jwt_audience)}

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
            options=options,
        )
    except jwt.ExpiredSignatureError as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        ) from exc

    exp = payload.get("exp")
    if exp is not None and isinstance(exp, (int, float)):
        if datetime.now(tz=timezone.utc).timestamp() > float(exp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )

    return payload


async def require_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> Dict[str, Any]:
    """FastAPI dependency enforcing JWT authenticated requests."""

    token = credentials.credentials
    return _decode_jwt(token)
