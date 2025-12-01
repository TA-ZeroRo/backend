"""Plogging API Endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID

from app.services.plogging_service import PloggingService
from app.schemas.plogging_schemas import (
    PloggingSessionCreate,
    PloggingSessionEnd,
    PloggingSessionResponse,
    PhotoVerificationRequest,
    PhotoVerificationResponse,
    MapRoutesResponse,
    UserPloggingStats,
)

router = APIRouter()
plogging_service = PloggingService()


# ===== 세션 관리 =====
@router.get("/sessions/active", response_model=Optional[PloggingSessionResponse])
async def get_active_session(user_id: UUID = Query(..., description="사용자 UUID")):
    """
    진행 중인 플로깅 세션 조회

    Parameters:
    - user_id: 사용자 UUID

    Returns:
    - 진행 중인 세션 정보 (없으면 null)
    """
    try:
        session = await plogging_service.plogging_repo.get_active_session(user_id)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions", response_model=PloggingSessionResponse, status_code=201)
async def start_plogging_session(request: PloggingSessionCreate):
    """
    플로깅 세션 시작

    Parameters:
    - user_id: 사용자 UUID

    Returns:
    - 생성된 세션 정보
    """
    try:
        session = await plogging_service.start_session(request.user_id)
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/sessions/{session_id}/end", response_model=PloggingSessionResponse)
async def end_plogging_session(session_id: int, request: PloggingSessionEnd):
    """
    플로깅 세션 종료 (GPS 경로 업로드)

    Parameters:
    - session_id: 세션 ID
    - route_points: GPS 경로 포인트 목록

    Returns:
    - 업데이트된 세션 정보 (포인트 포함)
    """
    try:
        session = await plogging_service.end_session(session_id, request.route_points)
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}/cancel")
async def cancel_plogging_session(session_id: int):
    """
    플로깅 세션 취소

    Parameters:
    - session_id: 세션 ID

    Returns:
    - 취소된 세션 정보
    """
    try:
        session = await plogging_service.cancel_session(session_id)
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=PloggingSessionResponse)
async def get_plogging_session(session_id: int):
    """
    플로깅 세션 상세 조회

    Parameters:
    - session_id: 세션 ID

    Returns:
    - 세션 정보
    """
    try:
        session = await plogging_service.plogging_repo.get_session_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== 사진 인증 =====
@router.post("/sessions/{session_id}/verify")
async def verify_plogging_photo(
    session_id: int,
    user_id: UUID,
    request: PhotoVerificationRequest
):
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
    try:
        result = await plogging_service.verify_photo(
            session_id=session_id,
            user_id=user_id,
            image_url=request.image_url,
            latitude=request.latitude,
            longitude=request.longitude
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== 지도 데이터 =====
@router.get("/map/routes", response_model=MapRoutesResponse)
async def get_map_routes(
    min_lat: Optional[float] = Query(None, description="최소 위도"),
    max_lat: Optional[float] = Query(None, description="최대 위도"),
    min_lng: Optional[float] = Query(None, description="최소 경도"),
    max_lng: Optional[float] = Query(None, description="최대 경도"),
    limit: int = Query(100, ge=1, le=500, description="최대 조회 개수")
):
    """
    지도에 표시할 경로 데이터 조회 (모든 사용자)

    Parameters:
    - min_lat, max_lat: 위도 범위
    - min_lng, max_lng: 경도 범위
    - limit: 최대 조회 개수

    Returns:
    - 커뮤니티 경로 목록
    """
    try:
        routes = await plogging_service.get_map_routes(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lng=min_lng,
            max_lng=max_lng,
            limit=limit
        )
        return routes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== 사용자 데이터 =====
@router.get("/users/{user_id}/sessions")
async def get_user_sessions(
    user_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    사용자 플로깅 세션 목록 조회

    Parameters:
    - user_id: 사용자 UUID
    - limit: 조회 개수
    - offset: 오프셋

    Returns:
    - 세션 목록 (최신순)
    """
    try:
        sessions = await plogging_service.get_user_sessions(user_id, limit, offset)
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/stats", response_model=UserPloggingStats)
async def get_user_plogging_stats(user_id: UUID):
    """
    사용자 플로깅 통계 조회

    Parameters:
    - user_id: 사용자 UUID

    Returns:
    - 총 세션 수, 총 시간, 총 거리, 총 인증 수, 총 포인트
    """
    try:
        stats = await plogging_service.get_user_stats(user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
