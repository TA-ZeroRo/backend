"""Base Repository 클래스"""
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from postgrest.exceptions import APIError
from app.core.config import get_supabase_config


class BaseRepository:
    """모든 Repository의 기본 클래스"""

    def __init__(self):
        SUPABASE_URL, SUPABASE_KEY = get_supabase_config()
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    async def find_by_id(self, table: str, id_value: str, id_column: str = "id") -> Optional[Dict[str, Any]]:
        """ID로 단일 레코드 조회"""
        try:
            response = (
                self.supabase
                .table(table)
                .select("*")
                .eq(id_column, id_value)
                .single()
                .execute()
            )
            return response.data if response.data else None
        except APIError as e:
            # PGRST116: 결과가 0개일 때 발생하는 에러
            if e.code == "PGRST116":
                return None
            raise  # 다른 에러는 그대로 전파

    async def find_all(self, table: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """모든 레코드 조회 (필터 적용 가능)"""
        query = self.supabase.table(table).select("*")

        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        response = query.execute()
        return response.data if response.data else []

    async def create(self, table: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """새 레코드 생성"""
        response = (
            self.supabase
            .table(table)
            .insert(data)
            .execute()
        )
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    async def update(self, table: str, id_value: str, data: Dict[str, Any], id_column: str = "id") -> Optional[Dict[str, Any]]:
        """레코드 업데이트"""
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
        """레코드 삭제"""
        response = (
            self.supabase
            .table(table)
            .delete()
            .eq(id_column, id_value)
            .execute()
        )
        return response.data is not None
