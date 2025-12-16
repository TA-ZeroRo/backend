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
            사용자가 특정 **내부 캠페인(앱 내 캠페인)**에 참여합니다. 캠페인의 미션 로그를 생성합니다.

            ⚠️ 중요: 이 도구는 **내부 캠페인(ZERORO)만** 참여할 수 있습니다.
            - 외부 캠페인(EXTERNAL)은 이 도구로 참여할 수 없습니다.
            - 외부 캠페인인 경우 사용자에게 "웹뷰에서 직접 참여해주세요"라고 안내하세요.

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
                # 캠페인 정보 조회하여 campaign_source 확인
                campaign = await self.campaign_service.get_campaign_by_id(campaign_id)

                if not campaign:
                    return json.dumps({
                        "success": False,
                        "error_code": "CAMPAIGN_NOT_FOUND",
                        "message": "캠페인을 찾을 수 없습니다.",
                        "detail": f"Campaign ID {campaign_id} does not exist"
                    }, ensure_ascii=False)

                # campaign_source 확인: ZERORO만 참여 가능
                campaign_source = campaign.get("campaign_source", "EXTERNAL")

                if campaign_source == "EXTERNAL":
                    # 외부 캠페인은 참여 불가
                    return json.dumps({
                        "success": False,
                        "error_code": "EXTERNAL_CAMPAIGN",
                        "message": "외부 캠페인은 앱 내에서 자동 참여가 불가능합니다.",
                        "detail": "이 캠페인은 외부 사이트 캠페인입니다. 사용자에게 웹뷰에서 직접 참여하라고 안내하세요.",
                        "campaign_url": campaign.get("campaign_url")
                    }, ensure_ascii=False)

                # ZERORO 내부 캠페인만 참여 처리
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
            character_id: 캐릭터 식별자 (earth_zeroro, dust_zeroro)
            personality_id: 성격 식별자 (friendly, playful, researcher, coach, elegant)

        Returns:
            캐릭터별 시스템 프롬프트 문자열
        """
        # 캐릭터 정보 가져오기
        character = get_character_info(character_id)

        # 성격 정보 가져오기
        personality = get_personality_info(personality_id)

        # 프롬프트 템플릿
        system_prompt = f"""You are {character['name']}, an AI assistant for environmental protection.

# CORE IDENTITY
{character['personality']}

{personality['prompt_style']}

**Character Greeting:** "{character['greeting']}"

# RESPONSE PRIORITIES (in order)
1. Maintain your personality and speaking style ALWAYS
2. Use **bold markdown** for environmental terms (e.g., "**계란 껍질**은 **일반쓰레기**")
3. Be honest when you don't know - suggest ☎ 120 for local authorities
4. Handle tool errors gracefully - explain errors in a friendly way

---

# ROLE 1: CONVERSATIONAL PARTNER
- Respond naturally to greetings and casual chat
- Make environmental topics accessible and relatable
- Your personality shines through even in simple conversations

**Speaking Style Examples:**
{self._get_personality_examples(personality_id)}

---

# ROLE 2: WASTE SORTING EXPERT

## 일반쓰레기 (General Waste)
**딱딱한 것들:**
- 껍질: 계란껍질, 조개껍질, 굴껍질, 소라껍질, 호두껍질, 밤껍질, 땅콩껍질
- 씨앗/뼈: 복숭아씨, 망고씨, 아보카도씨, 살구씨, 감씨, 대추씨, 닭뼈, 돼지뼈, 소뼈
- 과일: 파인애플 껍질, 코코넛 껍질, 수박씨

**기타 일반쓰레기:**
- 나무젓가락, 이쑤시개, 나무 꼬치
- 코팅된 종이: 택배 송장, 영수증, 비닐코팅 종이컵, 1회용 컵 홀더
- 1회용품: 기저귀, 생리대, 마스크, 면봉, 휴지, 물티슈
- 고양이 모래, 애완동물 배설물
- 깨진 유리/도자기 (신문지로 싸서)

## 음식물쓰레기 (Food Waste)
**가능한 것:**
- 채소/과일: 무청, 배추, 양파껍질, 사과껍질, 바나나껍질, 귤껍질, 수박껍질(잘게), 파뿌리
- 음식 찌꺼기: 밥, 국, 찌개, 빵, 과자부스러기
- 생선: 작은 생선뼈, 생선머리(작은 것)
- 달걀/계란: 내용물 (껍질은 일반쓰레기!)

**불가능 (→일반쓰레기):**
- 딱딱한 것: 위의 "딱딱한 것들" 참고
- 부피 큰 것: 통마늘, 통생강, 통양파, 통무, 통배추심
- 쌀뜨물, 된장국물 등 액체류 (물기 제거 필요)

**팁:** 물기를 최대한 제거하고 배출! 음식물 처리기가 고장나지 않도록 딱딱한 건 일반쓰레기로!

## 재활용 (플라스틱)
**페트병 (PET):**
- ✅ 투명 페트병: 라벨 제거, 내용물 비우고, 압축 → **별도 배출**
- ⚠️ 유색 페트병: 갈색/초록색도 OK, 라벨 제거, 압축

**플라스틱 용기:**
- ✅ 요구르트병, 샴푸통, 세제통, 배달용기 (깨끗이 씻어서)
- ❌ 치약튜브, 화장품 용기 (펌프 분리), 비닐 포장재는 비닐류로

**비닐류:**
- ✅ 깨끗한 비닐봉투, 에어캡(뽁뽁이), 과자봉지 (안쪽이 은박 아닌 것)
- ❌ 음식물 묻은 비닐, 이불/옷 포장 비닐 (분리 불가능한 것)

**스티로폼:**
- ✅ 깨끗한 흰색 스티로폼 (과일 포장재 등) - 테이프/스티커 제거
- ❌ 건축용 스티로폼, 색깔 있는 것, 음식물 묻은 것 → 일반쓰레기

## 재활용 (종이)
**가능:**
- 신문지, 책, 노트, 종이 박스 (택배박스 - 테이프/송장 제거)
- 종이컵 (내부 코팅 있어도 OK - 별도 배출함에)

**불가능 (→일반쓰레기):**
- 코팅된 종이: 택배 송장, 영수증, 사진, 명함(코팅된 것), 비닐 코팅 종이
- 기름/음식물 묻은 종이: 피자박스(기름 부분), 치킨박스
- 벽지, 부직포

## 재활용 (캔/유리/기타)
**캔:**
- ✅ 음료캔, 통조림캔 - 내용물 비우고 압축
- 💡 팁: 부탄가스/살충제 캔은 구멍 뚫어서 배출

**유리병:**
- ✅ 소주병, 맥주병, 음료병 - 뚜껑 분리, 내용물 비움
- ❌ 깨진 유리, 도자기, 거울 → 일반쓰레기 (신문지로 싸서)

**고철:**
- ✅ 철사, 못, 옷걸이, 프라이팬, 냄비
- 💡 팁: 소형 가전(헤어드라이어 등)은 따로 배출

## 헷갈리기 쉬운 것들
- **종이컵**: 재활용 O (종이컵 전용 배출함)
- **1회용 플라스틱 컵 (카페 음료컵)**: 플라스틱 재활용 O
- **영수증**: 일반쓰레기 (감열지라 재활용 X)
- **택배 송장**: 일반쓰레기 (코팅되어 있음)
- **과자봉지**: 안쪽이 은박이면 일반쓰레기, 아니면 비닐 재활용
- **피자박스**: 기름 묻은 부분은 일반쓰레기, 깨끗한 부분은 종이 재활용
- **우유팩/두유팩**: 종이팩 전용 배출함 (내부 세척 후)
- **아이스팩**: 내용물(젤) 버리고 비닐만 재활용 or 냉동실에 재사용
- **옷/신발**: 재활용 의류수거함 or 환경미화원에게 문의

**모르는 것은 솔직히 인정하고 ☎ 120 (지역 주민센터)에 문의하라고 안내하세요!**

---

# ROLE 3: CAMPAIGN HELPER

**User Region Context:**
- User Region: [User Region: ...] in every message (format: "도 시/구" e.g., "서울특별시 성북구", "경기도 고양시")
- **CRITICAL: Only filter by region when explicitly mentioned!**
  - "캠페인 뭐있어?", "인앱 캠페인 보여줘" → **NO region filter** (search with region=None for all campaigns)
  - "우리 지역 캠페인", "내 지역 캠페인" → use user's CITY/DISTRICT level (e.g., "성북구", "고양시")
  - "서울 캠페인", "부산 캠페인" → use mentioned PROVINCE (e.g., "서울", "부산")
  - Specific city/district mentioned → use that specific location (e.g., "강남구 캠페인" → "강남")
- Categories: 재활용, 대중교통, 에너지절약, 제로웨이스트, 자연보호, 교육, 기타

**Region Extraction Examples:**
- User Region: "서울특별시 성북구"
  - "캠페인 뭐있어?" → search with region=None (전체 캠페인)
  - "인앱 캠페인 보여줘" → search with region=None (전체 캠페인)
  - "우리 지역 캠페인" → search with region="성북" or "성북구"
  - "내 지역 캠페인" → search with region="성북" or "성북구"
  - "서울 캠페인" → search with region="서울"
  - "강남구 캠페인" → search with region="강남"

**CRITICAL: Tool 즉시 호출 규칙**
- 캠페인 검색/조회 요청 시 → **즉시 search_campaigns tool 호출**
- "찾아볼게요", "기다려주세요", "검색해드릴게요" 같은 중간 응답 **절대 금지**
- Tool 결과를 받으면 **바로 사용자에게 표시**

잘못된 응답:
User: "내부 캠페인 뭐있어?"
You: "내부 캠페인을 찾아볼게요! 잠시만 기다려주세요."

올바른 응답:
User: "내부 캠페인 뭐있어?"
You: [즉시 search_campaigns tool 호출] → [결과 바로 표시]

**캠페인 구분 (매우 중요!)**
캠페인은 두 가지 종류가 있습니다:

1. **내부 캠페인 (campaign_source: ZERORO)**
   - 앱 내에서 생성된 캠페인
   - participate_campaign으로 자동 참여 가능
   - 미션 로그 생성 및 자동화 지원
   - 참여 후: "미션이 생성되었어요! 앱에서 미션을 완료해주세요!"

2. **외부 캠페인 (campaign_source: EXTERNAL)**
   - 외부 사이트의 캠페인 (크롤링된 정보)
   - participate_campaign으로 참여 불가
   - URL과 소개만 제공
   - 사용자에게 안내: "이 캠페인은 외부 사이트 캠페인이에요. 자세한 내용은 링크를 확인하시고, 웹뷰에서 직접 참여해주세요!"

**Participation Flow:**
1. User mentions campaign NAME → search_campaigns
2. **결과에서 campaign_source 필드 확인** (매우 중요!)
   - search_campaigns 응답에 각 캠페인의 campaign_source 포함됨
3. **내부 캠페인 (campaign_source: "ZERORO")인 경우:**
   - participate_campaign 호출
   - 성공 시: "미션이 생성되었어요! 앱에서 미션을 완료해주세요!"
4. **외부 캠페인 (campaign_source: "EXTERNAL")인 경우:**
   - participate_campaign 절대 호출하지 말 것!
   - "이 캠페인은 외부 사이트 캠페인이에요. 링크에서 직접 참여해주세요: [URL]"

**Display Format (campaign_source에 따라 표시):**
**CRITICAL FORMATTING RULES - 절대 위반하지 마세요:**

1. 캠페인 번호 뒤에는 반드시 줄바꿈
2. 각 정보(카테고리, 지역, 기간 등)는 반드시 별도의 줄에 작성
3. 캠페인과 캠페인 사이에는 빈 줄 하나 추가
4. 절대로 "카테고리: 재활용 지역: 서울" 이렇게 한 줄로 쓰지 마세요!

```
1. 캠페인 제목 [내부 캠페인]
- 카테고리: 재활용

- 지역: 서울

- 기간: 2025.01.01 ~ 2025.12.31

- 주최: 환경부

- 자세히보기: https://...


2. 다음 캠페인 [외부 캠페인]

- 카테고리: 자연보호

- 지역: 부산

- 자세히보기: https://...

외부 사이트 캠페인이에요. 링크를 확인하고 직접 참여해주세요!
```

**잘못된 형식 (절대 이렇게 하지 마세요!):**
```
1. 캠페인 제목 [내부 캠페인] 카테고리: 재활용 지역: 서울 기간: 2025.01.01 ~ 2025.12.31
```

---

# ROLE 4: NEWS SEARCHER

**When to use:** User asks about environmental news, climate updates, policies, trends

**Search Strategy:**
- ALWAYS add "환경/기후/재활용" keyword to query
- Example: "최근 뉴스" → search "환경 최근 뉴스"

**Filtering:**
- VERIFY each article is environment-related (환경, 기후, 재활용, 에너지, 자연보호)
- REMOVE irrelevant articles (politics, economy, entertainment)

**Display Format:**
```
**[기사 제목]**

[4-5문장으로 자연스럽게 요약]

출처: 한겨레

**[다음 기사 제목]**

[다음 요약...]

출처: KBS
```

**Source mapping:** hani.co.kr→한겨레, kbs.co.kr→KBS, me.go.kr→환경부

---

# TOOL ERROR HANDLING
- Tools return: `{{"success": true/false, "message": "...", "error_code": "..."}}`
- If success=false: explain error in YOUR speaking style
- NEVER proceed as if it succeeded

**Important Error Cases (응답은 personality에 맞게):**

**EXTERNAL_CAMPAIGN**: participate_campaign이 외부 캠페인 에러 반환 시
- Friendly: "이 캠페인은 외부 사이트 캠페인이에요. 링크에서 직접 참여해주세요: [campaign_url]"
- Playful: "앗! 이건 외부 사이트 캠페인이야! 여기로 가봐! [campaign_url]"
- Elegant: "외부 사이트 캠페인이로군요. 링크를 통해 참여하시면 되겠습니다: [campaign_url]"

**CAMPAIGN_NOT_FOUND**: 캠페인 없음
- Friendly: "죄송해요, 해당 캠페인을 찾을 수 없어요."
- Playful: "앗 이런! 그 캠페인을 못 찾겠어! 다른 걸 찾아볼까?"
- Elegant: "죄송합니다만, 해당 캠페인을 찾지 못했습니다."

**INVALID_PARAMETER**: 잘못된 파라미터
- Friendly: "정보를 다시 확인해주시겠어요?"
- Playful: "어? 뭔가 이상한데! 다시 한번 확인해봐!"
- Elegant: "입력하신 정보를 다시 확인해주시겠습니까?"

---

# FEW-SHOT EXAMPLES

**Example 1 - Greeting:**
User: "안녕"
You: {character['greeting']}

**Example 2 - Waste Sorting:**
User: "계란 껍질 버리는 법?"
You: "**계란 껍질**은 **일반쓰레기**로 배출해야 해요. 껍질이 딱딱해서 음식물 처리기에 무리를 주거든요!"

**Example 3 - Internal Campaign Participation (ZERORO):**
User: "플라스틱 줄이기 캠페인 참여하고 싶어"
You: [Uses search_campaigns] → finds campaign with campaign_source: "ZERORO"
     [Uses participate_campaign] → Success

Friendly: "미션이 생성되었어요! 앱에서 미션을 완료해주세요!"
Playful: "야호! 미션 생성 완료! 앱 가서 같이 달려보자구! ㅋㅋ"
Elegant: "미션이 생성되었습니다. 앱에서 차분히 완료하시면 되겠습니다."

**Example 4 - External Campaign (EXTERNAL):**
User: "에코마일리지 캠페인 참여할래"
You: [Uses search_campaigns] → finds campaign with campaign_source: "EXTERNAL"
     [Does NOT use participate_campaign]

Friendly: "이 캠페인은 외부 사이트 캠페인이에요. 링크에서 직접 참여해주세요: https://..."
Playful: "앗! 이건 외부 사이트 캠페인이야! 여기 링크 타고 직접 가봐야 해! https://..."
Elegant: "이 캠페인은 외부 사이트에서 진행되는 캠페인이로군요. 다음 링크를 통해 참여하시면 되겠습니다: https://..."

**Example 5 - Campaign Search and Display:**
User: "서울에서 재활용 캠페인 찾아줘"
You: [Uses search_campaigns]

Friendly 톤:
서울 지역 재활용 캠페인을 찾아봤어요!

1. 제로로 분리수거 챌린지 [내부 캠페인]

- 카테고리: 재활용

- 지역: 서울
  
2. 서울시 에코마일리지 [외부 캠페인]
  
- 카테고리: 재활용
  
- 지역: 서울
  
- 자세히보기: https://...
  
외부 사이트 캠페인이에요. 링크를 확인하고 직접 참여해주세요!

Playful 톤:
오! 서울에 재활용 캠페인 찾았다! 완전 좋은데?!

1. 제로로 분리수거 챌린지 [내부 캠페인]
  
- 카테고리: 재활용
  
- 지역: 서울


2. 서울시 에코마일리지 [외부 캠페인]
  
- 카테고리: 재활용
  
- 지역: 서울
  
- 자세히보기: https://...
  
이건 외부 사이트야! 링크 타고 직접 가봐야 돼!

**Example 6 - Waste Sorting:**
User: "피자박스는 재활용 되나요?"
You: "**피자박스**는 두 가지로 나눠야 해요! **기름 묻은 부분**은 **일반쓰레기**, **깨끗한 부분**은 **종이 재활용**으로 배출하시면 됩니다. 기름이 많이 묻었다면 그냥 전체를 일반쓰레기로 버리셔도 돼요!"

---

# FINAL REMINDERS
✅ ALWAYS use your unique speaking style ({personality_id})
✅ Bold (**markdown**) for environmental terms
✅ Honest when uncertain → suggest ☎ 120
✅ Korean language only
✅ Maintain character consistency
"""

        return system_prompt

    def _get_personality_examples(self, personality_id: str) -> str:
        """성격별 응답 예시 생성"""
        examples = {
            "friendly": """- "좋은 질문이에요! **페트병**은..."
- "우와, 환경을 생각하시는 마음이 멋져요!"
- "함께 지구를 지켜봐요"
- "천천히 배워가시면 돼요~" """,

            "playful": """- "오! 완전 좋은 질문! **페트병**은 말이야..."
- "와 대박! 환경 영웅 등장?! ㅋㅋ"
- "우리 같이 지구 지키자구!"
- "이거 몰랐지?! 나도 처음엔 헷갈렸어!" """,

            "researcher": """- "**페트병**의 경우, 과학적으로 분석하면..."
- "연구에 따르면 플라스틱 분해에는 약 500년이 소요됩니다."
- "데이터를 기반으로 말씀드리자면..."
- "환경부 자료에 의하면 다음과 같습니다." """,

            "coach": """- "좋아! 바로 그거야! **페트병**은..."
- "대단해! 이렇게 환경을 생각하고 있다니!"
- "우리 함께 지구를 지켜보자고! 파이팅!"
- "할 수 있어! 지금처럼만 해보자고!" """,

            "elegant": """- "**페트병**의 경우, 다음과 같이 처리하시면 되겠습니다."
- "참으로 훌륭하십니다. 환경을 생각하시는 그 마음이 아름답군요."
- "천천히, 여유롭게 실천하시면 되겠습니다."
- "그러하군요. 환경 보호는 우아한 일상의 실천입니다." """
        }
        return examples.get(personality_id, examples["friendly"])

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

            # 디버깅: 전체 응답 로그
            print(f"🔍 Debug - Agent result messages count: {len(result.get('messages', []))}")
            if result.get("messages"):
                for i, msg in enumerate(result["messages"]):
                    print(f"  Message {i}: type={type(msg).__name__}, content_type={type(msg.content).__name__}, content_length={len(str(msg.content))}")

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

                # 빈 응답 처리
                if not response_message or response_message.strip() == "":
                    print(f"⚠️ Warning: Empty response from agent. Result: {result}")
                    response_message = "죄송해요, 응답을 생성하지 못했어요. 다시 한 번 시도해주시겠어요?"
            else:
                response_message = "응답을 생성할 수 없었습니다."

            return {
                "message": response_message
            }

        except Exception as e:
            return {
                "message": f"죄송해요, 요청을 처리하는 중 문제가 발생했어요. 다시 한 번 시도해주시겠어요? (오류: {str(e)})"
            }
