"""Agent Service - LangChain Agent를 사용한 AI 에이전트 대화 서비스"""
from typing import Dict, Any, Optional, List
from uuid import UUID
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.core.config import get_gemini_api_key
from app.services.campaign_service import CampaignService
from app.services.campaign_agent_service import CampaignAgentService


class AgentService:
    """AI 에이전트 대화 서비스 (LangChain Agent 기반)"""

    def __init__(self):
        self.campaign_service = CampaignService()
        self.campaign_agent_service = CampaignAgentService()

        # Gemini LLM 초기화
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=get_gemini_api_key(),
            temperature=0.7,
            convert_system_message_to_human=True
        )

        # Agent 초기화
        self.agent_executor = self._create_agent()

    def _create_agent(self):
        """LangGraph ReAct Agent 생성"""

        # Tools 정의 (클로저를 사용해서 self 접근)
        @tool
        async def get_campaigns(
            region: Optional[str] = None,
            category: Optional[str] = None,
            status: str = "ACTIVE"
        ) -> str:
            """
            사용자 지역, 카테고리, 상태에 맞는 환경 캠페인을 조회합니다.

            Args:
                region: 지역 (예: "서울", "부산", "경기" 등). 생략 시 전국 캠페인 조회
                category: 캠페인 카테고리. 다음 중 하나:
                    - RECYCLING: 재활용/분리수거
                    - TRANSPORTATION: 대중교통/자전거
                    - ENERGY: 에너지 절약
                    - ZERO_WASTE: 제로웨이스트/다회용기
                    - CONSERVATION: 자연보호/환경정화
                    - EDUCATION: 교육/세미나
                    - OTHER: 기타
                status: 캠페인 상태 (EXPECT: 예정, ACTIVE: 진행중, EXPIRED: 종료). 기본값은 ACTIVE

            Returns:
                JSON 형식의 캠페인 목록 문자열
            """
            try:
                result = await self.campaign_service.get_campaigns(
                    region=region,
                    category=category,
                    status=status,
                    offset=0
                )
                return json.dumps(result, ensure_ascii=False)
            except Exception as e:
                return json.dumps({"error": str(e)}, ensure_ascii=False)

        @tool
        async def start_campaign(
            campaign_id: int,
            user_id: str
        ) -> str:
            """
            사용자가 특정 캠페인에 참여합니다. 캠페인의 미션 로그를 생성합니다.

            Args:
                campaign_id: 참여할 캠페인 ID (정수)
                user_id: 사용자 UUID (문자열)

            Returns:
                JSON 형식의 미션 로그 생성 결과
            """
            try:
                result = await self.campaign_agent_service.start_campaign(
                    user_id=UUID(user_id),
                    campaign_id=campaign_id
                )
                return json.dumps(result, ensure_ascii=False, default=str)
            except Exception as e:
                return json.dumps({"error": str(e)}, ensure_ascii=False)

        # Tools 리스트
        tools = [get_campaigns, start_campaign]

        # System prompt for the agent
        system_prompt = """You are ZeroRo, a friendly AI assistant for an environmental protection app.
Help users find and participate in environmental campaigns.

Important Guidelines:
- Always respond in Korean with a friendly tone
- When showing campaign lists, number them for easy selection

# Your Role:
1. Campaign Search: Help users find campaigns based on region, category, or keywords
2. Campaign Participation: Help users join campaigns (creates mission logs)

# Campaign Participation Process:
1. If user mentions campaign by NAME (e.g., "분리수거 챌린지 참여"):
   - First, use get_campaigns to search for that campaign
   - Find the campaign_id from results
   - Then call start_campaign with the campaign_id

2. If user mentions by NUMBER/ORDER (e.g., "첫 번째 참여", "2번 참여"):
   - Extract campaign_id from previous conversation
   - Call start_campaign with the campaign_id

3. After successful participation:
   - Inform user that missions have been created
   - Guide them to check mission details in the app
   - Explain that missions (photos, quizzes, etc.) should be completed in the app UI

# Important Notes:
- Mission submissions (photos, quizzes, texts) are done through the app UI, not through chat
- Final RPA submission happens when user completes all missions via app button
- Focus on helping users discover and join campaigns, then guide them to the app for mission completion

- Encourage users to participate in environmental protection"""

        # LangGraph의 create_react_agent 사용
        agent_executor = create_react_agent(
            model=self.llm,
            tools=tools,
            prompt=system_prompt
        )

        return agent_executor

    async def chat(
        self,
        user_id: UUID,
        message: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        사용자와 AI 에이전트 대화

        Args:
            user_id: 사용자 UUID
            message: 사용자 메시지
            history: 대화 히스토리 (클라이언트가 관리)

        Returns:
            응답 딕셔너리 (message)
        """
        try:
            # 메시지 리스트 구성
            messages = []

            # 1. 이전 대화 히스토리 추가
            if history:
                for h in history:
                    # h는 ChatMessage 객체 또는 딕셔너리일 수 있음
                    if isinstance(h, dict):
                        role = h.get("role", "user")
                        content = h.get("content", "")
                    else:
                        # Pydantic 모델인 경우
                        role = h.role
                        content = h.content
                    messages.append((role, content))

            # 2. 현재 사용자 메시지 추가
            input_message = f"[User ID: {user_id}]\n{message}"
            messages.append(("user", input_message))

            # LangGraph의 invoke는 messages를 받음
            result = await self.agent_executor.ainvoke({
                "messages": messages
            })

            # 마지막 메시지에서 응답 추출
            if result.get("messages"):
                last_message = result["messages"][-1]

                # content가 리스트인 경우 (Tool 호출 포함)
                if isinstance(last_message.content, list):
                    # text 타입만 추출하여 결합
                    text_parts = [
                        part.get("text", "") if isinstance(part, dict) else str(part)
                        for part in last_message.content
                        if isinstance(part, dict) and part.get("type") == "text"
                    ]
                    response_message = "\n".join(text_parts) if text_parts else "응답을 생성할 수 없었습니다."
                else:
                    # content가 문자열인 경우
                    response_message = last_message.content
            else:
                response_message = "응답을 생성할 수 없었습니다."

            return {
                "message": response_message
            }

        except Exception as e:
            return {
                "message": f"죄송해요, 요청을 처리하는 중 문제가 발생했어요. 다시 한 번 시도해주시겠어요? (오류: {str(e)})"
            }
