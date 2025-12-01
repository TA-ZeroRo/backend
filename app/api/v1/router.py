from fastapi import APIRouter

# API v1 메인 라우터
router = APIRouter()

# TODO: 엔드포인트 파일들이 생성되면 주석을 해제 해야 함 - JOJO
from .endpoints import campaign, campaign_agent, agent, character, personality, community, leaderboard, like, point, users, verification, report, mission_log, rpa_webview, recruiting_chat, plogging

# 각 엔드포인트 라우터 등록 (파일 생성 후 활성화)
router.include_router(campaign.router, prefix="/campaign", tags=["Campaign"])
router.include_router(campaign_agent.router, prefix="/campaign-agent", tags=["Campaign Agent"])
router.include_router(agent.router, prefix="/agent", tags=["AI Agent"])
router.include_router(character.router, prefix="/character", tags=["Character"])
router.include_router(personality.router, prefix="/personality", tags=["Personality"])
router.include_router(community.router, prefix="/community", tags=["Community"])
router.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])
router.include_router(like.router, prefix="/like", tags=["Like"])
router.include_router(point.router, prefix="/point", tags=["Point"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(verification.router, prefix="/verification", tags=["Verification"])
router.include_router(report.router, prefix="/report", tags=["Report"])
# router.include_router(rpa.router, prefix="/rpa", tags=["RPA"])  # Deprecated: 2025-01-22 - Moved to WebView RPA
router.include_router(rpa_webview.router, prefix="/rpa-webview", tags=["WebView RPA"])  # New: 2025-01-22
router.include_router(mission_log.router, prefix="/mission-logs", tags=["Mission Logs"])
router.include_router(recruiting_chat.router, prefix="/recruiting", tags=["Recruiting Chat"])  # New: 2025-01-26
router.include_router(plogging.router, prefix="/plogging", tags=["Plogging"])  # New: 2025-12-01


# 임시 테스트 엔드포인트
@router.get("/test")
async def test_endpoint():
    return {"message": "API v1 router is working", "status": "success"}
