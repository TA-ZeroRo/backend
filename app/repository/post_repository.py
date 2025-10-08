"""Post Repository

Encapsulates Supabase operations for community posts.
Only post-related methods are included per migration scope.
"""
from typing import Optional, List, Dict, Any

from app.repository.base_repository import BaseRepository


class PostRepository(BaseRepository):
    POST_TABLE = "posts"

    async def get_post_by_id(self, post_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single post with joined profile fields."""
        response = (
            self.supabase
            .table(self.POST_TABLE)
            .select("*, profiles!posts_user_id_fkey(user_img, username)")
            .eq("id", post_id)
            .single()
            .execute()
        )
        return response.data if response.data else None

    async def get_all_posts(self) -> List[Dict[str, Any]]:
        """Fetch all posts ordered by creation time desc with joined profiles."""
        response = (
            self.supabase
            .table(self.POST_TABLE)
            .select("*, profiles!posts_user_id_fkey(user_img, username)")
            .order("created_at", desc=True)
            .execute()
        )
        return response.data if response.data else []

    async def create_post(self, post_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Insert a post and return the created record with profile join."""
        insert_response = (
            self.supabase
            .table(self.POST_TABLE)
            .insert(post_data)
            .execute()
        )
        if not insert_response.data or len(insert_response.data) == 0:
            return None
        created_post_id = insert_response.data[0]["id"]
        return await self.get_post_by_id(created_post_id)

    async def update_post(self, post_id: int, post_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        response = (
            self.supabase
            .table(self.POST_TABLE)
            .update(post_data)
            .eq("id", post_id)
            .execute()
        )
        if response.data and len(response.data) > 0:
            return await self.get_post_by_id(post_id)
        return None

    async def delete_post(self, post_id: int) -> bool:
        return await self.delete(self.POST_TABLE, str(post_id))

    async def increment_likes(self, post_id: int) -> bool:
        response = self.supabase.rpc("increment_likes", {"post_id": post_id}).execute()
        return response.data is not None

    async def decrement_likes(self, post_id: int) -> bool:
        response = self.supabase.rpc("decrement_likes", {"post_id": post_id}).execute()
        return response.data is not None

