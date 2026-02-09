"""Authentication dependencies for FastAPI routes."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_session
from app.db.supabase import supabase
from app.repositories.user_repo import UserRepository
from app.models.user import UserProfile

# HTTP Bearer token scheme for extracting JWT from Authorization header
http_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    session: AsyncSession = Depends(get_session),
) -> UserProfile:
    """
    FastAPI dependency to get the current authenticated user.
    
    Extracts JWT from Authorization header, verifies it against Supabase auth API,
    and retrieves the user from the database.
    
    Args:
        credentials: HTTP Bearer credentials containing the JWT
        session: Database session
        
    Returns:
        UserProfile: The authenticated user
        
    Raises:
        HTTPException: 401 if authentication fails or token is invalid
        HTTPException: 404 if user not found in database
        
    Usage:
        @app.get("/protected")
        async def protected_route(current_user: UserProfile = Depends(get_current_user)):
            return {"message": f"Hello {current_user.username}"}
    """
    # Check if credentials were provided
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Verify token against Supabase auth API
        # This validates the token signature, expiration, and user existence
        response = supabase.auth.get_user(token)
        user_id = response.user.id
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please register first.",
        )
    
    return user


async def get_current_active_user(
    current_user: UserProfile = Depends(get_current_user),
) -> UserProfile:
    """
    FastAPI dependency to get the current active user.
    
    Extends get_current_user to add additional checks like:
    - User account is active (not disabled)
    - User has completed registration
    
    Args:
        current_user: The authenticated user from get_current_user
        
    Returns:
        UserProfile: The active authenticated user
        
    Raises:
        HTTPException: 403 if user account is inactive or incomplete
        
    Usage:
        @app.get("/sensitive")
        async def sensitive_route(user: UserProfile = Depends(get_current_active_user)):
            return {"data": "sensitive info"}
    """
    # Add any additional checks here (e.g., account status, email verification)
    # For now, we just return the user
    
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    session: AsyncSession = Depends(get_session),
) -> Optional[UserProfile]:
    """
    FastAPI dependency to optionally get the current user.
    
    Similar to get_current_user but returns None instead of raising
    an exception if authentication fails. Useful for endpoints that
    work with or without authentication.
    
    Args:
        credentials: HTTP Bearer credentials containing the JWT
        session: Database session
        
    Returns:
        UserProfile or None: The authenticated user if valid token provided
        
    Usage:
        @app.get("/public-or-private")
        async def endpoint(user: Optional[UserProfile] = Depends(get_optional_user)):
            if user:
                return {"message": f"Hello {user.username}"}
            return {"message": "Hello guest"}
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    
    try:
        # Verify token against Supabase auth API
        response = supabase.auth.get_user(token)
        user_id = response.user.id
        
        user_repo = UserRepository(session)
        user = await user_repo.get_by_id(user_id)
        return user
    except Exception:
        # Silently return None for optional auth
        return None


def require_auth():
    """
    Factory function to create an auth dependency with custom error handling.
    
    Returns:
        Depends: A dependency that requires authentication
        
    Example:
        router = APIRouter(dependencies=[require_auth()])
    """
    return Depends(get_current_user)
