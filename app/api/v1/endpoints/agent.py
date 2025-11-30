"""Agent Endpoint - AI 에이전트 대화 API"""
from fastapi import APIRouter, HTTPException
from app.schemas.agent_schemas import ChatRequest, ChatResponse
from app.services.agent_service import AgentService

router = APIRouter()
agent_service = AgentService()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    AI 에이전트와 자연어 대화를 통해 캠페인 조회, 참여, 신청을 수행합니다.

    **사용 예시:**

    1. 캠페인 추천:
       - "서울에서 진행 중인 재활용 캠페인 추천해줘"
       - "대중교통 관련 캠페인 있어?"

    2. 캠페인 참여:
       - "첫 번째 캠페인 참여할래"
       - "에코마일리지 신청하고 싶어"

    **Parameters:**
    - user_id (UUID): 사용자 고유 ID
    - message (str): 사용자 메시지
    - selected_character (str, optional): 선택된 캐릭터 ID (기본값: earth_zeroro)
      - earth_zeroro (지구 제로로)
      - dust_zeroro (먼지 제로로)

    **Returns:**
    - message (str): AI 응답 메시지 (선택한 캐릭터의 말투로)
    """
    try:
        result = await agent_service.chat(
            user_id=request.user_id,
            message=request.message,
            selected_character=request.selected_character
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI 에이전트 처리 중 오류가 발생했습니다: {str(e)}"
        )
