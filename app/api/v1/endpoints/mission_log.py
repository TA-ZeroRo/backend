"""Mission Log API Endpoints"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.services.mission_log_service import MissionLogService
from app.schemas.mission_log_schemas import (
    MissionLogResponse,
    MissionLogStatus,
    MissionLogUpdate
)

router = APIRouter()
mission_log_service = MissionLogService()


@router.get("/users/{user_id}", response_model=List[MissionLogResponse])
async def get_mission_logs_by_user(user_id: UUID):
    """
    사용자의 모든 미션 로그 조회 (템플릿 및 캠페인 정보 포함)

    Parameters:
    - user_id: 사용자 UUID

    Returns:
    - 미션 로그 목록 (최신순, 템플릿 및 캠페인 정보 포함)
    """
    try:
        logs = await mission_log_service.get_mission_logs_by_user(user_id)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/{log_id}")
async def get_mission_log_by_id(log_id: int):
    """
    미션 로그 ID로 단일 로그 조회 (템플릿, 캠페인, 사용자 정보 포함)

    Parameters:
    - log_id: 미션 로그 ID

    Returns:
    - 미션 로그 정보
    """
    try:
        log = await mission_log_service.get_mission_log_by_id(log_id)
        if not log:
            raise HTTPException(status_code=404, detail="Mission log not found")
        return log
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{mission_template_id}")
async def get_mission_logs_by_template(mission_template_id: int):
    """
    미션 템플릿 ID로 미션 로그 목록 조회 (사용자 정보 포함)

    Parameters:
    - mission_template_id: 미션 템플릿 ID

    Returns:
    - 미션 로그 목록 (사용자 정보 포함)
    """
    try:
        logs = await mission_log_service.get_mission_logs_by_template(mission_template_id)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/status/{status}")
async def get_mission_logs_by_user_and_status(
    user_id: UUID,
    status: MissionLogStatus
):
    """
    사용자 ID와 상태로 미션 로그 목록 조회 (템플릿 및 캠페인 정보 포함)

    Parameters:
    - user_id: 사용자 UUID
    - status: 미션 상태 (IN_PROGRESS, PENDING_VERIFICATION, COMPLETED, FAILED)

    Returns:
    - 미션 로그 목록 (템플릿 및 캠페인 정보 포함)
    """
    try:
        logs = await mission_log_service.get_mission_logs_by_user_and_status(
            user_id,
            status.value
        )
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}")
async def get_mission_logs_by_campaign(
    campaign_id: int,
    user_id: Optional[UUID] = Query(None, description="특정 사용자로 필터링")
):
    """
    캠페인 ID로 미션 로그 목록 조회 (템플릿 및 사용자 정보 포함)

    Parameters:
    - campaign_id: 캠페인 ID
    - user_id: 특정 사용자로 필터링 (선택사항)

    Returns:
    - 미션 로그 목록 (템플릿 및 사용자 정보 포함)
    """
    try:
        logs = await mission_log_service.get_mission_logs_by_campaign(
            campaign_id,
            user_id=user_id
        )
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/templates/{mission_template_id}")
async def get_user_mission_by_template(
    user_id: UUID,
    mission_template_id: int
):
    """
    특정 사용자의 특정 미션 템플릿 로그 조회

    Parameters:
    - user_id: 사용자 UUID
    - mission_template_id: 미션 템플릿 ID

    Returns:
    - 미션 로그 정보 또는 None
    """
    try:
        log = await mission_log_service.get_user_mission_by_template(
            user_id,
            mission_template_id
        )
        if not log:
            raise HTTPException(
                status_code=404,
                detail="Mission log not found for this user and template"
            )
        return log
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logs/{log_id}/proof", response_model=MissionLogResponse)
async def submit_proof_data(
    log_id: int,
    proof_data: Dict[str, Any] = Body(...)
):
    """
    증빙 데이터 제출 및 상태 자동 변경

    증빙 데이터가 들어올 때 자동으로 상태를 판단합니다:
    - 정상 데이터: IN_PROGRESS -> COMPLETED
    - 오류 데이터: IN_PROGRESS -> FAILED

    Parameters:
    - log_id: 미션 로그 ID
    - proof_data: 증빙 데이터
      - 정상 완료 예시:
        {
          "images": ["url1", "url2"],
          "text": "미션 완료했습니다!"
        }
      - 실패 예시:
        {
          "error": "시스템 오류",
          "error_message": "상세 오류 내용"
        }

    Returns:
    - 업데이트된 미션 로그 정보
    """
    try:
        updated_log = await mission_log_service.submit_proof_data(
            log_id,
            proof_data
        )
        return updated_log
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/logs/{log_id}/status", response_model=MissionLogResponse)
async def update_mission_log_status(
    log_id: int,
    update_data: MissionLogUpdate = Body(...)
):
    """
    미션 로그 상태 수동 업데이트 (모든 상태 변경 가능)

    Parameters:
    - log_id: 미션 로그 ID
    - update_data: 상태 업데이트 데이터
      - status (필수): 변경할 상태 (모든 상태 허용)
      - proof_data (선택): 증빙 데이터
      - completed_at (선택): 완료 시간 (COMPLETED 상태일 때만 의미 있음)

    Returns:
    - 업데이트된 미션 로그 정보
    """
    if not update_data.status:
        raise HTTPException(status_code=400, detail="Status is required")

    try:
        updated_log = await mission_log_service.update_mission_log_status(
            log_id,
            update_data.status.value,
            proof_data=update_data.proof_data,
            completed_at=update_data.completed_at.isoformat() if update_data.completed_at else None
        )
        return updated_log
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))