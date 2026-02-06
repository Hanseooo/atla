from sqlmodel import SQLModel, Field, Relationship, Column
from typing import Optional, List
from datetime import datetime
from pydantic import EmailStr
from sqlalchemy.dialects.postgresql import JSONB


class UserProfile(SQLModel, table=True):
    """Extended user profile (auth.users managed by Supabase)"""
    __tablename__ = "user_profiles"
    
    id: str = Field(primary_key=True)  # Matches Supabase auth.users.id
    username: str = Field(unique=True, index=True, max_length=50)
    display_name: Optional[str] = Field(default=None, max_length=100)
    email: EmailStr
    avatar_url: Optional[str] = None
    preferences: dict = Field(default_factory=dict, sa_column=Column(JSONB, default=dict))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships (commented out until other models exist)
    # trips: List["Trip"] = Relationship(back_populates="user")
    # chat_sessions: List["ChatSession"] = Relationship(back_populates="user")
    # saved_places: List["SavedPlace"] = Relationship(back_populates="user")


# Response model (without sensitive data)
class UserProfilePublic(SQLModel):
    id: str
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime


# Create/Update models
class UserProfileCreate(SQLModel):
    username: str
    email: EmailStr
    display_name: Optional[str] = None


class UserProfileUpdate(SQLModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[dict] = None
