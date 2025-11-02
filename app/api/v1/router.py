from fastapi import APIRouter

# API v1 메인 라우터
router = APIRouter()

# TODO: 엔드포인트 파일들이 생성되면 주석을 해제 해야 함 - JOJO
from .endpoints import campaign, character, community, leaderboard, like, point, users, verification, report

# 각 엔드포인트 라우터 등록 (파일 생성 후 활성화)
router.include_router(campaign.router, prefix="/campaign", tags=["Campaign"])
router.include_router(character.router, prefix="/character", tags=["Character"])
router.include_router(community.router, prefix="/community", tags=["Community"])
router.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])
router.include_router(like.router, prefix="/like", tags=["Like"])
router.include_router(point.router, prefix="/point", tags=["Point"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(verification.router, prefix="/verification", tags=["Verification"])
router.include_router(report.router, prefix="/report", tags=["Report"])

# 임시 테스트 엔드포인트
@router.get("/test")
async def test_endpoint():
    return {"message": "API v1 router is working", "status": "success"}