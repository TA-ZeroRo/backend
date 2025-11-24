from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.services.campaign_service import CampaignService
from app.schemas.campaign_schemas import CampaignCategory, CampaignStatus, CampaignResponse

router = APIRouter()
campaign_service = CampaignService()


@router.get("/campaigns", response_model=List[CampaignResponse])
async def get_campaigns(
    region: Optional[str] = Query(None, description="지역 필터 (예: '서울특별시', '경기도')"),
    category: Optional[CampaignCategory] = Query(None, description="카테고리 필터"),
    status: Optional[CampaignStatus] = Query(None, description="상태 필터 (기본: ACTIVE)"),
    offset: int = Query(0, ge=0, description="페이지네이션 오프셋"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 조회 개수 (기본: 20, 최대: 100)")
):
    try:
        result = await campaign_service.get_campaigns(
            region=region,
            category=category.value if category else None,
            status=status.value if status else None,
            offset=offset,
            limit=limit
        )
        return result["campaigns"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
