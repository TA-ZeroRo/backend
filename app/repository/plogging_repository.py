"""Plogging Repository"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import date
from app.repository.base_repository import BaseRepository
from postgrest.exceptions import APIError


class PloggingRepository(BaseRepository):
    """플로깅 관련 데이터베이스 작업을 처리하는 Repository"""

    SESSIONS_TABLE = "plogging_sessions"
    ROUTES_TABLE = "plogging_routes"
    VERIFICATIONS_TABLE = "plogging_verifications"
    H3_TABLE = "plogging_h3_aggregations"

    # ===== 세션 관련 =====
    async def create_session(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """플로깅 세션 생성"""
        data = {"user_id": str(user_id)}
        return await self.create(self.SESSIONS_TABLE, data)

    async def get_session_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        """세션 ID로 조회"""
        try:
            response = (
                self.supabase
                .table(self.SESSIONS_TABLE)
                .select("*")
                .eq("id", session_id)
                .single()
                .execute()
            )
            return response.data if response.data else None
        except APIError as e:
            if e.code == "PGRST116":
                return None
            raise

    async def get_active_session(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """사용자의 진행 중인 세션 조회"""
        try:
            response = (
                self.supabase
                .table(self.SESSIONS_TABLE)
                .select("*")
                .eq("user_id", str(user_id))
                .eq("status", "IN_PROGRESS")
                .single()
                .execute()
            )
            return response.data if response.data else None
        except APIError as e:
            if e.code == "PGRST116":
                return None
            raise

    async def update_session(self, session_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """세션 업데이트"""
        return await self.update(self.SESSIONS_TABLE, str(session_id), data)

    async def get_sessions_by_user(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """사용자별 세션 목록 조회"""
        response = (
            self.supabase
            .table(self.SESSIONS_TABLE)
            .select("*")
            .eq("user_id", str(user_id))
            .order("started_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return response.data if response.data else []

    async def get_completed_sessions_in_area(
        self,
        min_lat: float,
        max_lat: float,
        min_lng: float,
        max_lng: float,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """특정 영역 내 완료된 세션 목록 조회 (경로 포함)"""
        response = (
            self.supabase
            .table(self.SESSIONS_TABLE)
            .select("*, plogging_routes(*)")
            .eq("status", "COMPLETED")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        # 영역 필터링 (route의 bounding box 기준)
        if response.data:
            filtered = []
            for session in response.data:
                routes = session.get("plogging_routes", [])
                if routes:
                    route = routes[0] if isinstance(routes, list) else routes
                    r_min_lat = route.get("min_lat")
                    r_max_lat = route.get("max_lat")
                    r_min_lng = route.get("min_lng")
                    r_max_lng = route.get("max_lng")

                    # 영역이 겹치는지 확인
                    if (r_min_lat and r_max_lat and r_min_lng and r_max_lng and
                        r_min_lat <= max_lat and r_max_lat >= min_lat and
                        r_min_lng <= max_lng and r_max_lng >= min_lng):
                        filtered.append(session)
            return filtered
        return []

    # ===== 경로 관련 =====
    async def create_route(
        self,
        session_id: int,
        route_points: List[Dict[str, Any]],
        min_lat: float,
        max_lat: float,
        min_lng: float,
        max_lng: float
    ) -> Optional[Dict[str, Any]]:
        """GPS 경로 저장"""
        data = {
            "session_id": session_id,
            "route_points": route_points,
            "point_count": len(route_points),
            "min_lat": min_lat,
            "max_lat": max_lat,
            "min_lng": min_lng,
            "max_lng": max_lng
        }
        return await self.create(self.ROUTES_TABLE, data)

    async def get_route_by_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """세션의 경로 조회"""
        try:
            response = (
                self.supabase
                .table(self.ROUTES_TABLE)
                .select("*")
                .eq("session_id", session_id)
                .single()
                .execute()
            )
            return response.data if response.data else None
        except APIError as e:
            if e.code == "PGRST116":
                return None
            raise

    # ===== 인증 관련 =====
    async def create_verification(
        self,
        session_id: int,
        user_id: UUID,
        latitude: float,
        longitude: float,
        image_url: str
    ) -> Optional[Dict[str, Any]]:
        """사진 인증 기록 생성"""
        data = {
            "session_id": session_id,
            "user_id": str(user_id),
            "latitude": latitude,
            "longitude": longitude,
            "image_url": image_url
        }
        return await self.create(self.VERIFICATIONS_TABLE, data)

    async def update_verification(
        self,
        verification_id: int,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """인증 결과 업데이트"""
        return await self.update(self.VERIFICATIONS_TABLE, str(verification_id), data)

    async def get_verifications_by_session(self, session_id: int) -> List[Dict[str, Any]]:
        """세션의 인증 목록 조회"""
        response = (
            self.supabase
            .table(self.VERIFICATIONS_TABLE)
            .select("*")
            .eq("session_id", session_id)
            .order("verified_at", desc=True)
            .execute()
        )
        return response.data if response.data else []

    # ===== H3 집계 관련 =====
    async def upsert_h3_aggregation(
        self,
        h3_index: str,
        aggregation_date: date,
        duration_minutes: int,
        intensity: int,
        center_lat: float,
        center_lng: float
    ) -> Optional[Dict[str, Any]]:
        """H3 그리드 집계 upsert"""
        # 기존 데이터 조회
        try:
            existing = (
                self.supabase
                .table(self.H3_TABLE)
                .select("*")
                .eq("h3_index", h3_index)
                .eq("aggregation_date", aggregation_date.isoformat())
                .single()
                .execute()
            )

            if existing.data:
                # 업데이트
                new_total = existing.data["total_sessions"] + 1
                new_duration = existing.data["total_duration_minutes"] + duration_minutes
                new_avg_intensity = (
                    (existing.data["avg_intensity"] * existing.data["total_sessions"]) + intensity
                ) / new_total

                return await self.update(
                    self.H3_TABLE,
                    str(existing.data["id"]),
                    {
                        "total_sessions": new_total,
                        "total_duration_minutes": new_duration,
                        "avg_intensity": new_avg_intensity
                    }
                )
        except APIError as e:
            if e.code != "PGRST116":
                raise

        # 새로 생성
        data = {
            "h3_index": h3_index,
            "aggregation_date": aggregation_date.isoformat(),
            "total_sessions": 1,
            "total_duration_minutes": duration_minutes,
            "avg_intensity": float(intensity),
            "center_lat": center_lat,
            "center_lng": center_lng
        }
        return await self.create(self.H3_TABLE, data)

    async def get_h3_aggregations(
        self,
        aggregation_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """H3 집계 데이터 조회"""
        query = self.supabase.table(self.H3_TABLE).select("*")

        if aggregation_date:
            query = query.eq("aggregation_date", aggregation_date.isoformat())

        response = query.execute()
        return response.data if response.data else []

    # ===== 통계 관련 =====
    async def get_user_stats(self, user_id: UUID) -> Dict[str, Any]:
        """사용자 플로깅 통계 조회"""
        response = (
            self.supabase
            .table(self.SESSIONS_TABLE)
            .select("*")
            .eq("user_id", str(user_id))
            .eq("status", "COMPLETED")
            .execute()
        )

        sessions = response.data if response.data else []

        total_duration = sum(s.get("duration_minutes", 0) or 0 for s in sessions)
        total_distance = sum(s.get("total_distance_meters", 0) or 0 for s in sessions)
        total_verifications = sum(s.get("verification_count", 0) or 0 for s in sessions)
        total_points = sum(s.get("points_earned", 0) or 0 for s in sessions)

        intensities = [s.get("intensity_level", 1) for s in sessions]
        avg_intensity = sum(intensities) / len(intensities) if intensities else 1.0

        return {
            "total_sessions": len(sessions),
            "total_duration_minutes": total_duration,
            "total_distance_meters": total_distance,
            "total_verifications": total_verifications,
            "total_points_earned": total_points,
            "avg_intensity_level": avg_intensity
        }
