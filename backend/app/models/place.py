from sqlmodel import SQLModel, Field, Relationship, Column
from typing import Optional, List
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB


class Place(SQLModel, table=True):
    """Destinations, restaurants, hotels, attractions"""
    __tablename__ = "places"
    
    id: str = Field(primary_key=True)  # External ID (Google Place ID, etc.)
    name: str = Field(index=True, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(default=None, index=True, max_length=50)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    website: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    price_level: Optional[int] = Field(default=None, ge=1, le=4)
    opening_hours: dict = Field(default_factory=dict, sa_column=Column(JSONB, default=dict))
    photos: List[str] = Field(default_factory=list, sa_column=Column(JSONB, default=list))
    place_metadata: dict = Field(default_factory=dict, sa_column=Column(JSONB, default=dict))
    source: Optional[str] = Field(default=None, max_length=50)  # 'brave_search', 'manual', etc.
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SavedPlace(SQLModel, table=True):
    """Places saved by users"""
    __tablename__ = "saved_places"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user_profiles.id", index=True)
    place_id: str = Field(foreign_key="places.id", index=True)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Response models
class PlacePublic(SQLModel):
    id: str
    name: str
    category: Optional[str]
    latitude: float
    longitude: float
    rating: Optional[float]


class PlaceDetail(PlacePublic):
    description: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    price_level: Optional[int]
    opening_hours: dict
    photos: List[str]
