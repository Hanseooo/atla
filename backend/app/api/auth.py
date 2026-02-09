"""Authentication router for user profile management."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from app.db.session import get_session
from app.db.supabase import supabase
from app.api.deps import get_current_user, get_optional_user
from app.repositories.user_repo import UserRepository
from app.models.user import UserProfile, UserProfilePublic, UserProfileCreate

router = APIRouter(prefix="/auth", tags=["authentication"])
http_bearer = HTTPBearer()


# Request/Response Models
class UsernameCheckRequest(BaseModel):
    """Request model for checking username availability."""
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")


class UsernameCheckResponse(BaseModel):
    """Response model for username availability check."""
    available: bool
    username: str
    message: str


class ProfileCreateRequest(BaseModel):
    """Request model for creating user profile after Supabase signup."""
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    display_name: Optional[str] = Field(None, max_length=100)


class ProfileUpdateRequest(BaseModel):
    """Request model for updating user profile."""
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = Field(None, max_length=500)
    preferences: Optional[dict] = None


class ProfileResponse(BaseModel):
    """Response model for user profile."""
    id: str
    username: str
    email: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


@router.get("/me", response_model=ProfileResponse)
async def get_current_user_profile(
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Get the current authenticated user's profile.
    
    Returns the user's profile information including username, email,
    and other profile details.
    
    **Requires authentication.**
    
    Returns:
        ProfileResponse: User profile data
        
    Example:
        ```bash
        curl -H "Authorization: Bearer <token>" http://localhost:8000/auth/me
        ```
    """
    return ProfileResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        display_name=current_user.display_name,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at.isoformat(),
    )


@router.get("/check-username", response_model=UsernameCheckResponse)
async def check_username_availability(
    username: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Check if a username is available for registration.
    
    This endpoint is public (does not require authentication) and should
    be called before attempting registration to validate username availability.
    
    Args:
        username: The username to check (as query parameter)
        
    Returns:
        UsernameCheckResponse: Availability status and message
        
    Example:
        ```bash
        curl "http://localhost:8000/auth/check-username?username=john_doe"
        ```
    """
    # Validate username format
    import re
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return UsernameCheckResponse(
            available=False,
            username=username,
            message="Username can only contain letters, numbers, and underscores.",
        )
    
    if len(username) < 3 or len(username) > 50:
        return UsernameCheckResponse(
            available=False,
            username=username,
            message="Username must be between 3 and 50 characters.",
        )
    
    user_repo = UserRepository(session)
    
    # Check if username exists (case-insensitive)
    exists = await user_repo.username_exists(username.lower())
    
    if exists:
        return UsernameCheckResponse(
            available=False,
            username=username,
            message="Username is already taken. Please choose another.",
        )
    
    return UsernameCheckResponse(
        available=True,
        username=username,
        message="Username is available!",
    )


@router.post("/profile", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_user_profile(
    request: ProfileCreateRequest,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a user profile after successful Supabase authentication.
    
    This endpoint should be called immediately after the user signs up
    with Supabase. It creates the user profile in our database and links
    it to the Supabase auth user via the JWT token.
    
    **Requires a valid Supabase JWT token in the Authorization header.**
    
    Args:
        request: Profile creation data (username, email)
        credentials: HTTP Bearer credentials with JWT token
        
    Returns:
        ProfileResponse: Created user profile
        
    Raises:
        HTTPException: 400 if username already taken
        HTTPException: 401 if invalid token
        HTTPException: 409 if profile already exists
        
    Example:
        ```bash
        curl -X POST http://localhost:8000/auth/profile \
          -H "Authorization: Bearer <supabase-jwt>" \
          -H "Content-Type: application/json" \
          -d '{
            "username": "john_doe",
            "email": "john@example.com"
          }'
        ```
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Supabase token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Verify token against Supabase auth API
        response = supabase.auth.get_user(token)
        user_id = response.user.id

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_repo = UserRepository(session)
    
    # Check if user profile already exists (created by database trigger)
    existing_user = await user_repo.get_by_id(user_id)
    
    if existing_user:
        # Profile exists (trigger created it), UPDATE it with username
        # This is the hybrid approach: trigger creates minimal profile, we enrich it
        
        # Check if username is already set (profile already completed)
        if existing_user.username:
            # Profile already completed, return it
            return ProfileResponse(
                id=existing_user.id,
                username=existing_user.username,
                email=existing_user.email,
                display_name=existing_user.display_name,
                avatar_url=existing_user.avatar_url,
                created_at=existing_user.created_at.isoformat(),
            )
        
        # Check if requested username is taken by another user
        if await user_repo.username_exists(request.username.lower()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{request.username}' is already taken.",
            )
        
        # Update the existing profile with username and other data
        existing_user.username = request.username.lower()
        existing_user.email = request.email.lower()
        if request.display_name:
            existing_user.display_name = request.display_name
        
        updated_user = await user_repo.update(existing_user)
        
        return ProfileResponse(
            id=updated_user.id,
            username=updated_user.username,
            email=updated_user.email,
            display_name=updated_user.display_name,
            avatar_url=updated_user.avatar_url,
            created_at=updated_user.created_at.isoformat(),
        )
    
    # Profile doesn't exist (no trigger or local dev), CREATE it
    # Check if username is taken (case-insensitive)
    if await user_repo.username_exists(request.username.lower()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{request.username}' is already taken.",
        )
    
    # Check if email is already registered
    if await user_repo.email_exists(request.email.lower()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{request.email}' is already registered.",
        )
    
    # Create the user profile
    new_user = UserProfile(
        id=user_id,
        username=request.username.lower(),  # Store username in lowercase
        email=request.email.lower(),
        display_name=request.display_name,
        avatar_url=None,
        preferences={},
    )
    
    created_user = await user_repo.create(new_user)
    
    return ProfileResponse(
        id=created_user.id,
        username=created_user.username,
        email=created_user.email,
        display_name=created_user.display_name,
        avatar_url=created_user.avatar_url,
        created_at=created_user.created_at.isoformat(),
    )


@router.patch("/profile", response_model=ProfileResponse)
async def update_user_profile(
    request: ProfileUpdateRequest,
    current_user: UserProfile = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Update the current user's profile.
    
    Allows updating email, avatar URL, and preferences.
    Note: Username cannot be changed after creation.
    
    **Requires authentication.**
    
    Args:
        request: Profile update data
        current_user: The authenticated user
        session: Database session
        
    Returns:
        ProfileResponse: Updated user profile
        
    Raises:
        HTTPException: 400 if email already taken
        HTTPException: 404 if user not found
        
    Example:
        ```bash
        curl -X PATCH http://localhost:8000/auth/profile \
          -H "Authorization: Bearer <token>" \
          -H "Content-Type: application/json" \
          -d '{
            "avatar_url": "https://example.com/avatar.jpg",
            "preferences": {"theme": "dark"}
          }'
        ```
    """
    user_repo = UserRepository(session)
    
    # Check if email is being changed and if it's already taken
    if request.email and request.email.lower() != current_user.email.lower():
        if await user_repo.email_exists(request.email.lower()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{request.email}' is already registered.",
            )
        current_user.email = request.email.lower()
    
    # Update other fields
    if request.avatar_url is not None:
        current_user.avatar_url = request.avatar_url
    
    if request.preferences is not None:
        current_user.preferences = request.preferences
    
    # Save changes
    updated_user = await user_repo.update(current_user)
    
    return ProfileResponse(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        display_name=updated_user.display_name,
        avatar_url=updated_user.avatar_url,
        created_at=updated_user.created_at.isoformat(),
    )
