from fastapi import APIRouter, HTTPException
from uuid import UUID
from app.services.mission_service import MissionService

router = APIRouter()

@router.get("/{user_id}")
async def get_missions(user_id: UUID):
    """
    사용자의 미션을 campaign_id별로 그룹화하여 조회합니다.

    Parameters:
    - user_id (UUID): 사용자 ID

    Returns:
    - dict: campaign_id별로 그룹화된 미션 목록
        - missions_by_campaign (dict): {campaign_id: [missions...]}
    """
    try:
        mission_service = MissionService()
        return await mission_service.get_missions_by_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
