"""Agent Service - LangChain Agent를 사용한 AI 에이전트 대화 서비스"""
from typing import Dict, Any, Optional, List
from uuid import UUID
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import get_gemini_api_key, get_tavily_api_key
from app.config.characters import get_character_info
from app.config.personalities import get_personality_info
from app.services.campaign_service import CampaignService
from app.services.campaign_agent_service import CampaignAgentService
from app.services.user_service import UserService


class AgentService:
    """AI 에이전트 대화 서비스 (LangChain Agent 기반)"""

    def __init__(self):
        self.campaign_service = CampaignService()
        self.campaign_agent_service = CampaignAgentService()
        self.user_service = UserService()

        # Gemini LLM 초기화
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=get_gemini_api_key(),
            temperature=0.7,
            convert_system_message_to_human=True
        )

        # 세션별 메모리 저장소 (RAM에 저장, DB 사용 안 함)
        self.store = {}

    def _get_tools(self):
        """Agent에서 사용할 Tools 정의 및 반환"""

        # Tools 정의 (클로저를 사용해서 self 접근)
        @tool
        async def search_campaigns(
            region: Optional[str] = None,
            category: Optional[str] = None,
            status: str = "ACTIVE"
        ) -> str:
            """
            사용자 지역, 카테고리, 상태에 맞는 환경 캠페인을 검색합니다.
            이 도구는 캠페인을 찾기만 하고, 참여하지는 않습니다.

            Args:
                region: 지역 (예: "서울", "부산", "경기" 등). 생략 시 전국 캠페인 조회
                category: 캠페인 카테고리. 다음 중 하나:
                    - 재활용: 재활용/분리수거
                    - 대중교통: 대중교통/자전거
                    - 에너지절약: 에너지 절약
                    - 제로웨이스트: 제로웨이스트/다회용기
                    - 자연보호: 자연보호/환경정화
                    - 교육: 교육/세미나
                    - 기타: 기타
                status: 캠페인 상태 (EXPECT: 예정, ACTIVE: 진행중, EXPIRED: 종료). 기본값은 ACTIVE

            Returns:
                JSON 형식의 표준화된 응답 문자열
                성공: {"success": true, "campaigns": [...], "total": N}
                실패: {"success": false, "error_code": "...", "message": "...", "detail": "..."}
            """
            try:
                result = await self.campaign_service.get_campaigns(
                    region=region,
                    category=category,
                    status=status,
                    offset=0
                )
                # 표준화된 성공 응답
                return json.dumps({
                    "success": True,
                    "campaigns": result.get("campaigns", []),
                    "total": result.get("total", 0)
                }, ensure_ascii=False)
            except ValueError as e:
                # 유효성 검증 오류
                return json.dumps({
                    "success": False,
                    "error_code": "INVALID_PARAMETER",
                    "message": "잘못된 파라미터입니다.",
                    "detail": str(e)
                }, ensure_ascii=False)
            except Exception as e:
                # 일반 오류
                return json.dumps({
                    "success": False,
                    "error_code": "INTERNAL_ERROR",
                    "message": "캠페인 조회 중 오류가 발생했습니다.",
                    "detail": str(e)
                }, ensure_ascii=False)

        @tool
        async def participate_campaign(
            user_id: str,
            campaign_id: int
        ) -> str:
            """
            사용자가 특정 캠페인에 참여합니다. 캠페인의 미션 로그를 생성합니다.

            주의: 이 도구를 사용하기 전에 먼저 search_campaigns로 캠페인을 찾아야 합니다.
            사용자가 캠페인 이름을 말한 경우, search_campaigns로 검색하여 campaign_id를 찾은 후 이 도구를 사용하세요.

            Args:
                user_id: 사용자 UUID (문자열)
                campaign_id: 참여할 캠페인 ID (정수, 필수)

            Returns:
                JSON 형식의 표준화된 응답 문자열
                성공: {"success": true, "data": {...}}
                실패: {"success": false, "error_code": "...", "message": "...", "detail": "..."}
            """
            try:
                # campaign_id로 참여 처리
                result = await self.campaign_agent_service.start_campaign(
                    user_id=UUID(user_id),
                    campaign_id=campaign_id
                )

                # 표준화된 성공 응답
                return json.dumps({
                    "success": True,
                    "data": result
                }, ensure_ascii=False, default=str)

            except ValueError as e:
                # UUID 변환 오류 등
                return json.dumps({
                    "success": False,
                    "error_code": "INVALID_USER_ID",
                    "message": "잘못된 사용자 ID입니다.",
                    "detail": str(e)
                }, ensure_ascii=False)
            except Exception as e:
                # 일반 오류
                return json.dumps({
                    "success": False,
                    "error_code": "INTERNAL_ERROR",
                    "message": "캠페인 참여 처리 중 오류가 발생했습니다.",
                    "detail": str(e)
                }, ensure_ascii=False)

        # LangChain 공식 Tavily 검색 Tool 생성
        tavily_search = TavilySearchResults(
            max_results=5,
            search_depth="advanced",
            include_domains=[
                "news.naver.com",
                "news.jtbc.co.kr",
                "news.kbs.co.kr",
                "yonhapnews.co.kr",
                "hani.co.kr",
                "donga.com",
                "chosun.com",
                "me.go.kr"  # 한국 주요 뉴스 사이트 및 환경부
            ],
            name="search_environmental_news",
            description="""환경 관련 최신 뉴스를 검색합니다.

사용자가 환경 이슈, 기후 변화, 재활용 정책 등 환경 관련 최신 동향이나 뉴스를 물어볼 때 사용하세요.

Args:
    query: 검색할 키워드 (예: "환경 보호", "기후 변화", "재활용 정책" 등)

Returns:
    뉴스 검색 결과 목록 (제목, URL, 내용 포함)"""
        )

        # Tools 리스트
        tools = [search_campaigns, participate_campaign, tavily_search]

        return tools

    def _get_character_prompt(self, character_id: str, personality_id: str = "friendly") -> str:
        """
        캐릭터 ID와 성격 ID에 맞는 시스템 프롬프트 생성

        Args:
            character_id: 캐릭터 식별자 (zeroro, eco_warrior, nature_sage, tech_green)
            personality_id: 성격 식별자 (friendly, playful, researcher, coach, elegant)

        Returns:
            캐릭터별 시스템 프롬프트 문자열
        """
        # 캐릭터 정보 가져오기
        character = get_character_info(character_id)

        # 성격 정보 가져오기
        personality = get_personality_info(personality_id)

        # 기본 프롬프트 템플릿 (캐릭터 성격 + 말투 스타일 주입)
        system_prompt = f"""You are {character['name']}, an AI assistant for environmental protection.

# Your Identity and Personality:
{character['personality']}

# Your Speaking Style:
{personality['prompt_style']}

# Your Main Roles:

## 1. Friendly Conversational Partner
- Respond naturally to greetings, casual conversations, and everyday chat
- ALWAYS maintain your character's personality and speaking style as defined above
- Make environmental topics feel accessible and relatable

## 2. Environmental Q&A Assistant
- Answer questions about environmental protection, recycling, and waste sorting
- **IMPORTANT**: When mentioning environmental terms or key concepts, use **bold markdown** for emphasis
  - Example: "**계란 껍질**은 **일반쓰레기**로 배출하세요", "**재활용**할 때는...", "**제로웨이스트**란..."
- Use the guidelines below; if item is NOT listed, be honest about not knowing
- NEVER make up information; suggest checking with local authorities (☎ 120)

## 3. Campaign Search & Participation
- Help users find campaigns based on region, category, or keywords
- Available categories: 재활용, 대중교통, 에너지절약, 제로웨이스트, 자연보호, 교육, 기타
- Each message includes [User Region: ...] - use this proactively when recommending campaigns
- If user asks for campaigns without specifying region, use their region by default

## 4. Environmental News Search
- When users ask about environmental news, climate change updates, recycling policies, or recent environmental trends, use search_environmental_news tool
- **IMPORTANT**: Always add "환경" or "기후" or "재활용" keyword to the search query to ensure environmental relevance
  - Example: If user asks "최근 뉴스", search for "환경 최근 뉴스" instead
- After getting search results, **VERIFY** each article is actually related to environment (환경, 기후, 재활용, 에너지, 자연보호 등)
- Filter out articles that are NOT environmentally relevant (e.g., general politics, economy, entertainment)
- **CRITICAL FORMAT**: When displaying news results, use this EXACT format for EACH article:

  ```
  **[제목]**
  [내용을 3-5문장으로 요약. 각 문장은 새로운 줄로 구분하지 말고 자연스럽게 이어서 작성.]
  출처: [뉴스사이트명]

  ---

  **[다음 제목]**
  [다음 내용 요약]
  출처: [다음 뉴스사이트명]
  ```

  **중요**:
  - 제목은 첫째 줄에 굵게(**제목**) 표시
  - 내용은 둘째 줄부터 3-5문장으로 자연스럽게 작성
  - 출처는 마지막 줄에 "출처: 사이트명" 형식으로 표시
  - 각 뉴스 항목 사이는 "---"로 구분
  - 제목, 내용, 출처 사이에는 빈 줄을 넣지 말 것

- Extract news source from URL: "hani.co.kr" → "한겨레", "kbs.co.kr" → "KBS", "me.go.kr" → "환경부", etc.
- Provide 3-5 sentence summary for each article's content in a single paragraph
- **FORMAT RULES**:
  * First line: Bold title (**title**)
  * Second line onwards: Content summary (3-5 sentences, no line breaks within content)
  * Last line: Source in format "출처: [site name]"
  * Separator between articles: "---" on its own line with blank lines above and below
- If NO environmentally relevant articles are found, inform user politely

## 5. Tool Response Handling
- All tools return: `{{"success": true/false, ...}}`
- If `success == false`: Read `message` and `error_code`, explain to user in a friendly way
- NEVER ignore errors or proceed as if operation succeeded

# Common Waste Sorting Guidelines (Korea):

**일반쓰레기:**
- 딱딱한 껍질류: 계란껍질, 조개껍질, 굴껍질, 호두껍질
- 딱딱한 씨앗류: 복숭아씨, 망고씨, 아보카도씨
- 나무젓가락, 이쑤시개
- 코팅된 종이, 영수증, 비닐 코팅 종이컵

**음식물쓰레기:**
- 채소/과일 껍질 (단, 딱딱한 것 제외)
- 생선 가시 (작은 것)
- 달걀 내용물
- 주의: 딱딱하거나 날카로운 것은 처리기를 손상시킬 수 있어 일반쓰레기

**재활용 (플라스틱):**
- 플라스틱 병: 내용물 비우고, 라벨 제거, 압축
- 깨끗한 비닐류
- 투명 페트병은 별도 배출

**재활용 (종이):**
- 깨끗한 종이, 박스
- 불가: 코팅된 종이, 기름 묻은 종이

**재활용 (기타):**
- 캔: 내용물 비우고 압축
- 유리병: 내용물 비우고 뚜껑 분리
- 스티로폼: 깨끗한 것만, 테이프/이물질 제거

# Important Guidelines:
- Always respond in Korean with a friendly tone
- When showing campaign lists, use numbered format WITHOUT bullet points or dashes:
  ```
  1. 캠페인 제목
  카테고리: 재활용
  지역: 지역 이름
  기간: 2025.01.01 ~ 2025.12.31
  주최: 주최 단체
  장소: 캠페인 장소
  자세히보기: 해당 캠페인 URL

  2. 다음 캠페인 제목
  카테고리: 자연보호
  지역: 부산
  기간: 2025.02.01 ~ 2025.03.01
  주최: 주최 단체
  장소: 캠페인 장소
  자세히보기: 해당 캠페인 URL
  ```
  IMPORTANT: Do NOT use dashes (-) before each detail line. Write details directly without any bullet points.
- Use ONLY the waste sorting information above; if not listed, be honest and suggest checking ☎ 120
- NEVER fabricate or guess information

# Campaign Participation:
1. If user mentions campaign by NAME: search with search_campaigns, then call participate_campaign
2. If user mentions by NUMBER/ORDER: extract campaign_id from conversation, then call participate_campaign
3. After participation: inform user missions are created, guide them to check in the app
4. Note: Mission submissions (photos, quizzes) are done in app UI, not through chat

# Character-Specific Greeting:
When greeting users, use: "{character['greeting']}"

# Example Responses (maintain your character's style):

User: "안녕"
You: {character['greeting']}

User: "계란 껍질이 일반 쓰레기야?"
You: [Answer using your character's speaking style] "**계란 껍질**은 **일반쓰레기**로 배출해야 합니다. 껍질이 딱딱해서 음식물 처리기에 무리를 주기 때문입니다."

# Important Reminder:
- ALWAYS speak in your character's unique style and tone
- Maintain consistency with your personality throughout the conversation
"""

        return system_prompt

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
        selected_character: str = "earth_zeroro",
        selected_personality: str = "friendly"
    ) -> Dict[str, Any]:
        """
        사용자와 AI 에이전트 대화 (캐릭터별 개성, 서버 메모리에서 맥락 자동 관리)

        Args:
            user_id: 사용자 UUID
            message: 사용자 메시지
            selected_character: 선택된 캐릭터 ID (기본값: earth_zeroro)
            selected_personality: 선택된 성격 ID (기본값: friendly)

        Returns:
            응답 딕셔너리 (message)
        """
        try:
            # 세션 ID로 사용자 ID 사용
            session_id = str(user_id)

            # 사용자 지역 정보 조회
            user_region = "알 수 없음"
            try:
                user_info = await self.user_service.get_user_by_id(user_id)
                user_region = user_info.get("region", "알 수 없음")
            except Exception:
                # 사용자 정보 조회 실패 시 기본값 사용
                pass

            # 캐릭터별 프롬프트 생성 (성격 포함)
            character_prompt = self._get_character_prompt(selected_character, selected_personality)

            # 캐릭터 프롬프트로 에이전트 생성
            tools = self._get_tools()

            agent_executor = create_react_agent(
                model=self.llm,
                tools=tools,
                prompt=SystemMessage(content=character_prompt)
            )

            # 에이전트를 메모리 래퍼로 감싸기
            agent_with_memory = RunnableWithMessageHistory(
                agent_executor,
                self._get_session_history,
                input_messages_key="messages",
                output_messages_key="messages",
            )

            # 현재 메시지에 사용자 컨텍스트 추가
            input_message = f"[User ID: {user_id}]\n[User Region: {user_region}]\n{message}"

            # 메모리가 적용된 agent 실행
            result = await agent_with_memory.ainvoke(
                {"messages": [HumanMessage(content=input_message)]},
                config={"configurable": {"session_id": session_id}}
            )

            # 마지막 메시지에서 응답 추출
            if result.get("messages"):
                last_message = result["messages"][-1]

                # content를 항상 문자열로 변환
                if isinstance(last_message.content, str):
                    response_message = last_message.content
                elif isinstance(last_message.content, list):
                    # 리스트인 경우 'text' 타입의 content만 추출
                    text_parts = []
                    for item in last_message.content:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            text_parts.append(item.get('text', ''))
                        elif isinstance(item, str):
                            text_parts.append(item)
                    response_message = ''.join(text_parts)
                else:
                    # 기타 타입은 문자열로 변환
                    response_message = str(last_message.content)
            else:
                response_message = "응답을 생성할 수 없었습니다."

            return {
                "message": response_message
            }

        except Exception as e:
            return {
                "message": f"죄송해요, 요청을 처리하는 중 문제가 발생했어요. 다시 한 번 시도해주시겠어요? (오류: {str(e)})"
            }
