"""Point API Endpoints"""
from fastapi import APIRouter, HTTPException, Query
from uuid import UUID
from typing import List, Dict, Any
from app.services.point_service import PointService
from app.schemas.point_schemas import (
    PointTrendResponse,
    PointLogCreate,
    PointLogResponse
)

router = APIRouter()
point_service = PointService()


@router.get("/trend/{user_id}", response_model=PointTrendResponse)
async def get_point_trend(
    user_id: UUID,
    days: int = Query(default=7, ge=1, le=90, description="조회할 일수 (1~90일)")
) -> PointTrendResponse:
    """
    사용자의 포인트 추이 조회 (최근 N일)

    Parameters:
    -----------
    - user_id: 사용자 UUID
    - days: 조회할 일수 (기본값: 7일, 최소: 1일, 최대: 90일)

    Returns:
    --------
    - user_id: 사용자 ID
    - days: 조회 기간
    - data: 일별 포인트 데이터 리스트
      - date: 날짜 (YYYY-MM-DD)
      - total_points: 해당 날짜까지의 누적 포인트

    Example Response:
    ```json
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "days": 7,
      "data": [
        {"date": "2025-01-14", "total_points": 1000},
        {"date": "2025-01-15", "total_points": 1050},
        ...
      ]
    }
    ```
    """
    try:
        return await point_service.get_point_trend(user_id, days)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"포인트 추이 조회 실패: {str(e)}")


@router.get("/logs/{user_id}", response_model=List[PointLogResponse])
async def get_point_logs(
    user_id: UUID,
    limit: int = Query(default=50, ge=1, le=100, description="조회할 개수 (1~100개)")
) -> List[Dict[str, Any]]:
    """
    사용자의 포인트 로그 조회

    Parameters:
    -----------
    - user_id: 사용자 UUID
    - limit: 조회할 최대 개수 (기본값: 50개, 최소: 1개, 최대: 100개)

    Returns:
    --------
    포인트 로그 리스트 (최신순)
    - id: 로그 ID
    - user_id: 사용자 ID
    - point: 포인트 (양수: 획득, 음수: 사용)
    - description: 포인트 변동 사유
    - created_at: 생성 일시
    """
    try:
        return await point_service.get_point_logs(user_id, limit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"포인트 로그 조회 실패: {str(e)}")


@router.post("/logs", response_model=PointLogResponse, status_code=201)
async def create_point_log(
    log_data: PointLogCreate
) -> Dict[str, Any]:
    """
    포인트 로그 생성 (관리자/시스템 전용)

    Parameters:
    -----------
    - user_id: 사용자 UUID
    - point: 포인트 (양수: 획득, 음수: 사용, 0은 불가)

    Returns:
    --------
    생성된 포인트 로그

    Example Request:
    ```json
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "point": 100
    }
    ```
    """
    try:
        return await point_service.create_point_log(
            log_data.user_id,
            log_data.point
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"포인트 로그 생성 실패: {str(e)}")


