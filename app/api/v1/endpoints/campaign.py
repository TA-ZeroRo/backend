from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.campaign_service import CampaignService
from app.schemas.campaign_schemas import CampaignCategory, CampaignStatus

router = APIRouter()
campaign_service = CampaignService()


@router.get("/campaigns")
async def get_campaigns(
    region: Optional[str] = Query(None, description="지역 필터 (예: '서울특별시', '경기도')"),
    category: Optional[CampaignCategory] = Query(None, description="카테고리 필터"),
    status: Optional[CampaignStatus] = Query(None, description="상태 필터 (기본: ACTIVE)"),
    offset: int = Query(0, ge=0, description="페이지네이션 오프셋")
):
    """
    캠페인 목록을 조회합니다.

    Parameters:
    - region (str, optional): 지역 필터 (예: "서울특별시", "경기도")
    - category (CampaignCategory, optional): 카테고리 필터
      - RECYCLING: 재활용/분리수거
      - TRANSPORTATION: 대중교통/자전거
      - ENERGY: 에너지 절약
      - ZERO_WASTE: 제로웨이스트/다회용기
      - CONSERVATION: 자연보호/환경정화
      - EDUCATION: 교육/세미나
      - OTHER: 기타
    - status (CampaignStatus, optional): 상태 필터
      - EXPECT: 예정
      - ACTIVE: 진행중 (기본값)
      - EXPIRED: 종료
    - offset (int): 페이지네이션 시작 인덱스 (0부터 시작)

    Returns:
    - campaigns (List[CampaignResponse]): 캠페인 목록 (최신순, 페이지당 20개)

    Examples:
    - GET /campaigns - 진행중인 모든 캠페인
    - GET /campaigns?region=서울특별시 - 서울 지역 캠페인만
    - GET /campaigns?category=RECYCLING - 재활용 카테고리만
    - GET /campaigns?region=서울특별시&category=ENERGY - 서울 + 에너지절약
    - GET /campaigns?status=EXPECT - 예정된 캠페인만
    - GET /campaigns?offset=20 - 21번째부터 20개 조회
    """
    try:
        return await campaign_service.get_campaigns(
            region=region,
            category=category.value if category else None,
            status=status.value if status else None,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
