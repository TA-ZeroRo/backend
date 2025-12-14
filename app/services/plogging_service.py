"""Plogging Service - 플로깅 비즈니스 로직"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, date, timezone
from math import radians, cos, sin, asin, sqrt
import re

from app.repository.plogging_repository import PloggingRepository
from app.repository.user_repository import UserRepository
from app.services.plogging_ai_service import PloggingAIService
from app.schemas.plogging_schemas import (
    PloggingStatus,
    VerificationStatus,
    GpsPoint,
    PloggingSessionResponse,
    PhotoVerificationResponse,
    UserPloggingStats,
    CommunityRoute,
    MapRoutesResponse,
)


class PloggingService:
    """플로깅 관련 비즈니스 로직"""

    # 포인트 설정
    VERIFICATION_POINTS = 50  # 인증당 50P
    COMPLETION_BONUS = 100    # 완료 보너스 100P

    # 색상 농도 레벨 (분 기준)
    INTENSITY_THRESHOLDS = [
        (20, 1),   # 0-20분: 레벨 1 (연한 연두)
        (40, 2),   # 20-40분: 레벨 2 (중간 초록)
        (60, 3),   # 40-60분: 레벨 3 (진한 초록)
        (float('inf'), 4),  # 60분+: 레벨 4 (숲색)
    ]

    def __init__(self):
        self.plogging_repo = PloggingRepository()
        self.user_repo = UserRepository()
        self.ai_service = PloggingAIService()

    # ===== 세션 관리 =====
    async def start_session(self, user_id: UUID) -> Dict[str, Any]:
        """
        플로깅 세션 시작

        Parameters:
        - user_id: 사용자 UUID

        Returns:
        - 생성된 세션 정보
        """
        # 이미 진행 중인 세션이 있는지 확인
        active_session = await self.plogging_repo.get_active_session(user_id)
        if active_session:
            raise ValueError("이미 진행 중인 플로깅 세션이 있습니다.")

        # 새 세션 생성
        session = await self.plogging_repo.create_session(user_id)
        if not session:
            raise Exception("세션 생성에 실패했습니다.")

        return session

    async def end_session(
        self,
        session_id: int,
        route_points: List[GpsPoint]
    ) -> Dict[str, Any]:
        """
        플로깅 세션 종료

        Parameters:
        - session_id: 세션 ID
        - route_points: GPS 경로 포인트 목록

        Returns:
        - 업데이트된 세션 정보 (포인트 포함)
        """
        # 세션 조회
        session = await self.plogging_repo.get_session_by_id(session_id)
        if not session:
            raise ValueError("세션을 찾을 수 없습니다.")

        if session["status"] != PloggingStatus.IN_PROGRESS.value:
            raise ValueError("진행 중인 세션만 종료할 수 있습니다.")

        # 시간 계산 (Supabase 타임스탬프 포맷 호환)
        started_at = self._parse_timestamp(session["started_at"])
        ended_at = datetime.now(timezone.utc)
        duration = ended_at - started_at
        duration_minutes = int(duration.total_seconds() / 60)

        # 거리 계산
        total_distance = self._calculate_total_distance(route_points)

        # 색상 농도 레벨 계산
        intensity_level = self._calculate_intensity_level(duration_minutes)

        # 포인트 계산
        verification_count = session.get("verification_count", 0)
        points_earned = (verification_count * self.VERIFICATION_POINTS) + self.COMPLETION_BONUS

        # 세션 업데이트
        update_data = {
            "status": PloggingStatus.COMPLETED.value,
            "ended_at": ended_at.isoformat(),
            "duration_minutes": duration_minutes,
            "total_distance_meters": total_distance,
            "intensity_level": intensity_level,
            "points_earned": points_earned,
        }
        updated_session = await self.plogging_repo.update_session(session_id, update_data)

        # GPS 경로 저장
        if route_points:
            route_points_dict = [
                {
                    "lat": p.lat,
                    "lng": p.lng,
                    "timestamp": p.timestamp.isoformat(),
                    "accuracy": p.accuracy
                }
                for p in route_points
            ]

            lats = [p.lat for p in route_points]
            lngs = [p.lng for p in route_points]

            await self.plogging_repo.create_route(
                session_id=session_id,
                route_points=route_points_dict,
                min_lat=min(lats),
                max_lat=max(lats),
                min_lng=min(lngs),
                max_lng=max(lngs)
            )

        # 사용자 포인트 업데이트
        user_id = UUID(session["user_id"])
        await self._add_user_points(user_id, points_earned)

        return updated_session

    async def cancel_session(self, session_id: int) -> Dict[str, Any]:
        """세션 취소"""
        session = await self.plogging_repo.get_session_by_id(session_id)
        if not session:
            raise ValueError("세션을 찾을 수 없습니다.")

        if session["status"] != PloggingStatus.IN_PROGRESS.value:
            raise ValueError("진행 중인 세션만 취소할 수 있습니다.")

        update_data = {
            "status": PloggingStatus.CANCELLED.value,
            "ended_at": datetime.now().isoformat(),
        }

        return await self.plogging_repo.update_session(session_id, update_data)

    # ===== 사진 인증 =====
    async def verify_photo(
        self,
        session_id: int,
        user_id: UUID,
        image_url: str,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        플로깅 사진 AI 검증

        Parameters:
        - session_id: 세션 ID
        - user_id: 사용자 UUID
        - image_url: 이미지 URL
        - latitude: 위도
        - longitude: 경도

        Returns:
        - 검증 결과 (포인트 포함)
        """
        # 세션 확인
        session = await self.plogging_repo.get_session_by_id(session_id)
        if not session:
            raise ValueError("세션을 찾을 수 없습니다.")

        if session["status"] != PloggingStatus.IN_PROGRESS.value:
            raise ValueError("진행 중인 세션에서만 인증할 수 있습니다.")

        # 인증 기록 생성 (PENDING 상태)
        verification = await self.plogging_repo.create_verification(
            session_id=session_id,
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            image_url=image_url
        )

        # AI 검증 수행
        ai_result = await self.ai_service.verify_plogging_image(image_url)
        is_passed = self.ai_service.is_verification_passed(ai_result)

        # 인증 결과 업데이트
        verification_status = VerificationStatus.VERIFIED if is_passed else VerificationStatus.REJECTED
        points_earned = self.VERIFICATION_POINTS if is_passed else 0

        update_data = {
            "verification_status": verification_status.value,
            "ai_confidence": ai_result.confidence,
            "ai_result": {
                "is_valid": ai_result.is_valid,
                "confidence": ai_result.confidence,
                "detected_items": ai_result.detected_items,
                "reason": ai_result.reason
            }
        }
        updated_verification = await self.plogging_repo.update_verification(
            verification["id"],
            update_data
        )

        # 성공 시 세션 인증 횟수 증가
        if is_passed:
            await self.plogging_repo.update_session(
                session_id,
                {"verification_count": session.get("verification_count", 0) + 1}
            )

        return {
            **updated_verification,
            "points_earned": points_earned,
            "ai_result": ai_result.model_dump()
        }

    # ===== 지도 데이터 =====
    async def get_map_routes(
        self,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lng: Optional[float] = None,
        max_lng: Optional[float] = None,
        limit: int = 100
    ) -> MapRoutesResponse:
        """
        지도에 표시할 경로 데이터 조회

        Parameters:
        - min_lat, max_lat, min_lng, max_lng: 조회 영역
        - limit: 최대 조회 개수

        Returns:
        - 커뮤니티 경로 목록
        """
        # 기본값: 서울 영역
        if min_lat is None:
            min_lat = 37.4
        if max_lat is None:
            max_lat = 37.7
        if min_lng is None:
            min_lng = 126.8
        if max_lng is None:
            max_lng = 127.2

        sessions = await self.plogging_repo.get_completed_sessions_in_area(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lng=min_lng,
            max_lng=max_lng,
            limit=limit
        )

        routes = []
        for session in sessions:
            route_data = session.get("plogging_routes", [])
            if route_data:
                route = route_data[0] if isinstance(route_data, list) else route_data
                route_points = route.get("route_points", [])

                if route_points:
                    routes.append(CommunityRoute(
                        session_id=session["id"],
                        user_id=UUID(session["user_id"]),
                        intensity_level=session.get("intensity_level", 1),
                        route_points=[
                            GpsPoint(
                                lat=p["lat"],
                                lng=p["lng"],
                                timestamp=datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")),
                                accuracy=p.get("accuracy")
                            )
                            for p in route_points
                        ],
                        created_at=datetime.fromisoformat(
                            session["created_at"].replace("Z", "+00:00")
                        )
                    ))

        return MapRoutesResponse(
            routes=routes,
            total_count=len(routes)
        )

    # ===== 사용자 통계 =====
    async def get_user_stats(self, user_id: UUID) -> UserPloggingStats:
        """사용자 플로깅 통계 조회"""
        stats = await self.plogging_repo.get_user_stats(user_id)
        return UserPloggingStats(**stats)

    async def get_user_sessions(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """사용자 세션 목록 조회"""
        return await self.plogging_repo.get_sessions_by_user(user_id, limit, offset)

    # ===== Helper Methods =====
    def _calculate_intensity_level(self, duration_minutes: int) -> int:
        """시간 기반 색상 농도 레벨 계산"""
        for threshold, level in self.INTENSITY_THRESHOLDS:
            if duration_minutes < threshold:
                return level
        return 4  # 기본값

    def _calculate_total_distance(self, points: List[GpsPoint]) -> float:
        """GPS 포인트로부터 총 이동 거리 계산 (미터)"""
        if len(points) < 2:
            return 0.0

        total = 0.0
        for i in range(1, len(points)):
            total += self._haversine(
                points[i-1].lat, points[i-1].lng,
                points[i].lat, points[i].lng
            )
        return total

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """두 좌표 간 거리 계산 (Haversine, 미터)"""
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371000  # 지구 반경 (미터)
        return c * r

    @staticmethod
    def _parse_timestamp(ts: str) -> datetime:
        """Supabase 타임스탬프 파싱 (마이크로초 자릿수 정규화)"""
        # 마이크로초 부분을 6자리로 정규화
        # 예: '2025-12-14T09:34:57.78631+00:00' -> '2025-12-14T09:34:57.786310+00:00'
        match = re.match(r'(.+\.)(\d+)(\+.+)', ts)
        if match:
            prefix, microsec, suffix = match.groups()
            microsec = microsec.ljust(6, '0')[:6]  # 6자리로 맞춤
            ts = f"{prefix}{microsec}{suffix}"
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))

    async def _add_user_points(self, user_id: UUID, points: int) -> None:
        """사용자 포인트 추가"""
        user = await self.user_repo.get_user_by_id(str(user_id))
        if user:
            current_points = user.get("total_points", 0) or 0
            await self.user_repo.update_user(
                str(user_id),
                {"total_points": current_points + points}
            )
