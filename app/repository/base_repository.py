"""Base repository abstraction backed by Supabase."""
from typing import Optional, List, Dict, Any

from supabase import Client, create_client

from app.core.config import get_supabase_config


class BaseRepository:
    """Base class for repositories providing a Supabase client and helpers."""

    def __init__(self) -> None:
        supabase_url, supabase_key = get_supabase_config()
        self.supabase: Client = create_client(supabase_url, supabase_key)

    async def find_by_id(
        self, table: str, id_value: str, id_column: str = "id"
    ) -> Optional[Dict[str, Any]]:
        response = (
            self.supabase
            .table(table)
            .select("*")
            .eq(id_column, id_value)
            .single()
            .execute()
        )
        return response.data if response.data else None

    async def find_all(
        self, table: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        query = self.supabase.table(table).select("*")
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        response = query.execute()
        return response.data if response.data else []

    async def create(self, table: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        response = self.supabase.table(table).insert(data).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    async def update(
        self, table: str, id_value: str, data: Dict[str, Any], id_column: str = "id"
    ) -> Optional[Dict[str, Any]]:
        response = (
            self.supabase
            .table(table)
            .update(data)
            .eq(id_column, id_value)
            .execute()
        )
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    async def delete(self, table: str, id_value: str, id_column: str = "id") -> bool:
        response = (
            self.supabase
            .table(table)
            .delete()
            .eq(id_column, id_value)
            .execute()
        )
        return response.data is not None

