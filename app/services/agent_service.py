"""Agent Service - LangChain Agent를 사용한 AI 에이전트 대화 서비스"""
from typing import Dict, Any, Optional, List
from uuid import UUID
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage

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

        # 세션별 메모리 저장소 (RAM에 저장, DB 사용 안 함)
        self.store = {}

        # Agent 초기화
        self.agent_executor = self._create_agent()

        # Agent를 메모리 래퍼로 감싸기 (대화 맥락 자동 관리)
        self.agent_with_memory = RunnableWithMessageHistory(
            self.agent_executor,
            self._get_session_history,
            input_messages_key="messages",
            output_messages_key="messages",
        )

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
            user_id: str,
            campaign_id: Optional[int] = None,
            campaign_name: Optional[str] = None
        ) -> str:
            """
            사용자가 특정 캠페인에 참여합니다. 캠페인의 미션 로그를 생성합니다.

            Args:
                user_id: 사용자 UUID (문자열)
                campaign_id: 참여할 캠페인 ID (정수, 선택) - campaign_name과 둘 중 하나 필수
                campaign_name: 참여할 캠페인 이름 (문자열, 선택) - campaign_id와 둘 중 하나 필수

            Returns:
                JSON 형식의 미션 로그 생성 결과
            """
            try:
                # 1. 둘 다 없으면 에러
                if not campaign_id and not campaign_name:
                    return json.dumps({
                        "error": "campaign_id 또는 campaign_name 중 하나는 필수입니다."
                    }, ensure_ascii=False)

                # 2. campaign_name이 주어진 경우 → ID로 변환
                if campaign_name and not campaign_id:
                    # 캠페인 이름으로 검색
                    search_result = await self.campaign_service.get_campaigns(
                        status="ACTIVE",
                        offset=0
                    )

                    campaigns = search_result.get("campaigns", [])

                    # 이름이 정확히 일치하는 캠페인 찾기 (대소문자 무시)
                    matched_campaign = None
                    for campaign in campaigns:
                        if campaign["name"].lower() == campaign_name.lower():
                            matched_campaign = campaign
                            break

                    # 정확히 일치하는 게 없으면 부분 일치 검색
                    if not matched_campaign:
                        for campaign in campaigns:
                            if campaign_name.lower() in campaign["name"].lower():
                                matched_campaign = campaign
                                break

                    if not matched_campaign:
                        return json.dumps({
                            "error": f"'{campaign_name}' 캠페인을 찾을 수 없습니다. 정확한 캠페인 이름을 확인해주세요."
                        }, ensure_ascii=False)

                    campaign_id = matched_campaign["id"]

                # 3. campaign_id로 참여 처리
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

    def _get_session_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """
        세션 ID로 대화 히스토리 가져오기

        Args:
            session_id: 사용자 ID (세션 식별자)

        Returns:
            InMemoryChatMessageHistory 객체
        """
        if session_id not in self.store:
            self.store[session_id] = InMemoryChatMessageHistory()
        return self.store[session_id]

    async def chat(
        self,
        user_id: UUID,
        message: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        사용자와 AI 에이전트 대화 (서버 메모리에서 맥락 자동 관리)

        Args:
            user_id: 사용자 UUID
            message: 사용자 메시지
            history: (deprecated) 서버에서 자동으로 관리

        Returns:
            응답 딕셔너리 (message)
        """
        try:
            # 세션 ID로 사용자 ID 사용
            session_id = str(user_id)

            # 현재 메시지만 전달 (과거 대화는 메모리에서 자동으로 로드)
            input_message = f"[User ID: {user_id}]\n{message}"

            # 메모리가 적용된 agent 실행
            result = await self.agent_with_memory.ainvoke(
                {"messages": [HumanMessage(content=input_message)]},
                config={"configurable": {"session_id": session_id}}
            )

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
