"""Post-related Pydantic Schemas (Community Domain)

This module defines schemas used for community posts.
Only post-related models are included per migration scope.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel


class PostBase(BaseModel):
    """Base fields shared by post requests/responses."""
    title: str
    content: str
    image_url: Optional[str] = None


class PostCreate(PostBase):
    """Schema for creating a post."""
    user_id: UUID


class PostUpdate(BaseModel):
    """Schema for partially updating a post."""
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None


class PostResponse(PostBase):
    """Response schema for a post, including metadata and joined profile info."""
    id: int
    user_id: UUID
    likes_count: int = 0
    created_at: datetime
    profiles: Optional[Dict[str, Any]] = None  # e.g., {"user_img": ..., "username": ...}

    class Config:
        # Pydantic v2 compatibility for ORM-like objects
        from_attributes = True

