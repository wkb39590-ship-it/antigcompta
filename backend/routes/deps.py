from fastapi import Header, HTTPException
from typing import Dict

try:
    # reuse the simple decoder from auth.py
    from routes.auth import decode_jwt_token
except Exception:
    # fallback: import relative
    from .auth import decode_jwt_token


def get_current_session(authorization: str = Header(None)) -> Dict:
    """Decode session_token from Authorization header `Bearer <token>`.

    Returns the token payload as a dict and raises 401 if invalid/missing.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    token = parts[1]
    data = decode_jwt_token(token)
    if not data.get("societe_id"):
        raise HTTPException(status_code=401, detail="Session token missing societe context")
    return data
