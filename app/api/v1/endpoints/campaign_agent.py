from fastapi import APIRouter, HTTPException, Body, Query
from uuid import UUID
from typing import Dict, Any
from app.services.campaign_agent_service import CampaignAgentService
from app.schemas.mission_log_schemas import MissionLogResponse

router = APIRouter()
campaign_agent_service = CampaignAgentService()


# -------------------------
# --- START: 캠페인 진행 API ---
# -------------------------
@router.post("/campaigns/{campaign_id}", status_code=201)
async def start_campaign(campaign_id: int, user_id: UUID = Body(..., embed=True)):
    """
    사용자가 캠페인을 시작하고 모든 미션 로그를 생성합니다.

    Parameters:
    - campaign_id (int): 캠페인 ID
    - user_id (UUID): 사용자 ID (요청 본문)

    Returns:
    - campaign_info: 캠페인 정보
    - mission_logs: 생성된 미션 로그 목록
    """
    try:
        return await campaign_agent_service.start_campaign(user_id, campaign_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}")
async def get_campaign_progress(campaign_id: int, user_id: UUID = Query(...)):
    """
    사용자의 캠페인 진행 상황을 조회합니다.

    Parameters:
    - campaign_id (int): 캠페인 ID
    - user_id (UUID): 사용자 ID (쿼리 파라미터)

    Returns:
    - campaign_info: 캠페인 정보
    - progress_summary: 진행률 요약 (완료/전체)
    - mission_logs: 각 미션의 상태 및 상세 정보
    """
    try:
        return await campaign_agent_service.get_user_campaign_progress(user_id, campaign_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/campaigns/{campaign_id}", status_code=200)
async def cancel_campaign(campaign_id: int, user_id: UUID = Body(..., embed=True)):
    """
    사용자의 캠페인 참가를 취소하고 모든 미션 로그를 삭제합니다.

    Parameters:
    - campaign_id (int): 캠페인 ID
    - user_id (UUID): 사용자 ID (요청 본문)

    Returns:
    - success: 성공 여부
    - deleted_count: 삭제된 미션 로그 개수
    - message: 결과 메시지
    """
    try:
        return await campaign_agent_service.cancel_campaign(user_id, campaign_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# -----------------------
# --- END: 캠페인 진행 API ---
# -----------------------


# -----------------------
# --- START: 미션 제출 API ---
# -----------------------
@router.post("/mission-logs/{mission_log_id}", response_model=MissionLogResponse)
async def submit_mission_with_rpa(
    mission_log_id: int,
    user_id: UUID = Body(...),
    submission_data: Dict[str, Any] = Body(...),
    credentials: Dict[str, str] = Body(...)
):
    """
    RPA를 통해 미션을 제출합니다.

    Parameters:
    - mission_log_id (int): 미션 로그 ID
    - user_id (UUID): 사용자 ID
    - submission_data (dict): 제출할 폼 데이터
      - name (str): 신청자 이름
      - birth (str): 생년월일 (6자리)
      - phone (str): 전화번호
      - activity_date (str): 활동일자 (YYYY-MM-DD)
      - activity_content (str): 활동내용
    - credentials (dict): 로그인 인증 정보
      - username (str): 사용자명
      - password (str): 비밀번호

    Returns:
    - MissionLogResponse: 업데이트된 미션 로그 정보
    """
    try:
        return await campaign_agent_service.submit_mission_with_rpa(
            user_id=user_id,
            mission_log_id=mission_log_id,
            submission_data=submission_data,
            credentials=credentials
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/mission-logs/{mission_log_id}", response_model=MissionLogResponse)
async def retry_failed_mission(
    mission_log_id: int,
    user_id: UUID = Body(...),
    submission_data: Dict[str, Any] = Body(...),
    credentials: Dict[str, str] = Body(...)
):
    """
    실패한 미션을 재시도합니다.

    Parameters:
    - mission_log_id (int): 미션 로그 ID
    - user_id (UUID): 사용자 ID
    - submission_data (dict): 제출할 폼 데이터
    - credentials (dict): 로그인 인증 정보

    Returns:
    - MissionLogResponse: 업데이트된 미션 로그 정보
    """
    try:
        return await campaign_agent_service.submit_mission_with_rpa(
            user_id=user_id,
            mission_log_id=mission_log_id,
            submission_data=submission_data,
            credentials=credentials
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ---------------------
# --- END: 미션 제출 API ---
# ---------------------
