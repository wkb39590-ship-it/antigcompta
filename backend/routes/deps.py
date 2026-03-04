from fastapi import Header, HTTPException, Depends, Query
from typing import Dict, Optional

try:
    from routes.auth import decode_jwt_token, get_current_agent
except Exception:
    from .auth import decode_jwt_token, get_current_agent


def get_current_session(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None),
) -> Dict:
    """Decode session_token from Authorization header `Bearer <token>`
    OR from `?token=<token>` query param (used by legacy pages).

    Returns the token payload as a dict and raises 401 if invalid/missing.
    """
    raw_token = None

    # 1. Priorité : Authorization: Bearer <token>
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            raw_token = parts[1]
        else:
            raise HTTPException(status_code=401, detail="Invalid authorization header format")

    # 2. Fallback : ?token=<token> (query param)
    elif token:
        raw_token = token

    else:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    data = decode_jwt_token(raw_token)
    if not data.get("societe_id"):
        raise HTTPException(status_code=401, detail="Session token missing societe context")
    return data


def require_admin(agent=Depends(get_current_agent)):
    """Dependency helper: ensures the current agent is an admin."""
    if not getattr(agent, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return agent
