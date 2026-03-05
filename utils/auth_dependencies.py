"""
Authentication dependencies for securing API endpoints.
This module provides FastAPI dependency functions to verify JWT tokens.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

security = HTTPBearer()

# These should match your auth service settings
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY must be set in environment variables")


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Verify JWT token and extract payload.
    
    This is a lightweight verification that only validates the token signature
    and expiry. It does NOT check session revocation status in the database.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        Dict containing token payload (user_id, jti, etc.)
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verify token type
        if payload.get("type") != "access":
            raise credentials_exception
        
        # Extract user_id and jti
        sub = payload.get("sub")
        try:
            user_id = int(sub) if sub is not None else None
        except (TypeError, ValueError):
            user_id = None
            
        jti: str = payload.get("jti")
        
        if user_id is None or jti is None:
            raise credentials_exception
            
        return {
            "user_id": user_id,
            "jti": jti,
            "payload": payload
        }
        
    except JWTError:
        raise credentials_exception
    except Exception:
        raise credentials_exception


async def get_current_user_id(
    token_data: Dict[str, Any] = Depends(verify_token)
) -> int:
    """
    Extract and return the current user ID from the verified token.
    
    Use this dependency when you need the user ID for your endpoint.
    
    Example:
        @app.post("/api/generate-questions")
        async def generate_questions(
            request: QuestionRequest,
            user_id: int = Depends(get_current_user_id)
        ):
            # Your endpoint logic here
            # You can use user_id to track who made the request
            pass
    """
    return token_data["user_id"]


async def get_token_payload(
    token_data: Dict[str, Any] = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Get the full token payload.
    
    Use this if you need access to additional token data beyond just user_id.
    """
    return token_data["payload"]


async def require_authentication(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> bool:
    """
    Simple dependency to require authentication without extracting user data.
    Returns True if token is valid.
    
    Use this when you just need to ensure the endpoint is protected
    but don't need the user information.
    
    Example:
        @app.get("/api/health")
        async def protected_health(auth: bool = Depends(require_authentication)):
            return {"status": "healthy"}
    """
    await verify_token(credentials)
    return True
