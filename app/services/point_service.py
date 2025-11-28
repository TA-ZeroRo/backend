"""Point Service - 포인트 관련 비즈니스 로직"""
from fastapi import HTTPException
from uuid import UUID
from typing import Dict, Any, List
from app.repository.point_log_repository import PointLogRepository
from app.schemas.point_schemas import PointTrendResponse, PointTrendDataPoint


class PointService:
    """포인트 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        self.point_repo = PointLogRepository()

    async def get_point_trend(
        self,
        user_id: UUID,
        days: int = 7
    ) -> PointTrendResponse:
        """
        사용자의 포인트 추이 조회

        Parameters:
        -----------
        user_id : UUID
            사용자 ID
        days : int
            조회할 일수 (기본값: 7일, 최대: 90일)

        Returns:
        --------
        PointTrendResponse
            포인트 추이 응답 객체
        """
        # 조회 기간 검증
        if days < 1:
            raise HTTPException(
                status_code=400,
                detail="조회 기간은 최소 1일 이상이어야 합니다."
            )
        if days > 90:
            raise HTTPException(
                status_code=400,
                detail="조회 기간은 최대 90일까지 가능합니다."
            )

        # Repository에서 일별 포인트 데이터 조회
        daily_data = await self.point_repo.get_daily_point_trend(user_id, days)

        # PointTrendDataPoint 객체로 변환
        data_points = [
            PointTrendDataPoint(
                date=item["date"],
                total_points=item["total_points"]
            )
            for item in daily_data
        ]

        # 응답 객체 생성
        return PointTrendResponse(
            user_id=user_id,
            days=days,
            data=data_points
        )

    async def get_point_logs(
        self,
        user_id: UUID,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        사용자의 포인트 로그 조회

        Parameters:
        -----------
        user_id : UUID
            사용자 ID
        limit : int
            조회할 최대 개수 (기본값: 50개, 최대: 100개)

        Returns:
        --------
        List[Dict[str, Any]]
            포인트 로그 리스트
        """
        # 조회 개수 검증
        if limit < 1:
            raise HTTPException(
                status_code=400,
                detail="조회 개수는 최소 1개 이상이어야 합니다."
            )
        if limit > 100:
            raise HTTPException(
                status_code=400,
                detail="조회 개수는 최대 100개까지 가능합니다."
            )

        # Repository에서 포인트 로그 조회
        logs = await self.point_repo.get_logs_by_user(user_id, limit)
        return logs

    async def create_point_log(
        self,
        user_id: UUID,
        point: int
    ) -> Dict[str, Any]:
        """
        포인트 로그 생성

        Parameters:
        -----------
        user_id : UUID
            사용자 ID
        point : int
            포인트 (양수: 획득, 음수: 사용)

        Returns:
        --------
        Dict[str, Any]
            생성된 포인트 로그
        """
        # 포인트 검증
        if point == 0:
            raise HTTPException(
                status_code=400,
                detail="포인트는 0이 아니어야 합니다."
            )

        # Repository에서 포인트 로그 생성
        log = await self.point_repo.create_point_log(user_id, point)
        if not log:
            raise HTTPException(
                status_code=500,
                detail="포인트 로그 생성에 실패했습니다."
            )

        return log
