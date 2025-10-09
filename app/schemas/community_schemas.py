"""Community domain: Post-related Pydantic schemas.

This module intentionally includes only Post schemas for stepwise migration.
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


# ===== Post Schemas =====
class PostBase(BaseModel):
    """Base fields shared by Post requests/responses."""
    title: str
    content: str
    image_url: Optional[str] = None


class PostCreate(PostBase):
    """Schema for creating a Post."""
    user_id: UUID


class PostUpdate(BaseModel):
    """Schema for partially updating a Post."""
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None


class PostResponse(PostBase):
    """Response schema for a Post, including metadata and joined profile info."""
    id: int
    user_id: UUID
    likes_count: int = 0
    created_at: datetime
    profiles: Optional[Dict[str, Any]] = None  # e.g., {"user_img": ..., "username": ...}

    class Config:
        from_attributes = True

