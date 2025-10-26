"""Verification Service - 인증 관련 비즈니스 로직"""
from fastapi import HTTPException
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
import json
from enum import IntEnum
from dataclasses import dataclass

from app.core.config import get_gemini_api_key
from app.repository.base_repository import BaseRepository


# ===== 카테고리 정의 =====
class MainCategory(IntEnum):
    """메인 카테고리"""
    PROPER_DISPOSAL = 0
    REUSABLE_ITEMS = 1
    RESOURCE_SAVING = 2
    SUGGESTION = 3

    @property
    def display_name(self) -> str:
        """카테고리의 한글 이름 반환"""
        names = {
            0: '올바른 분리배출',
            1: '다회용품 사용',
            2: '자원 절약 및 재활용',
            3: '건의하기'
        }
        return names[self.value]


@dataclass
class SubCategory:
    """서브 카테고리"""
    id: int
    name: str
    main_category: MainCategory

    @property
    def main_category_id(self) -> int:
        """메인 카테고리 ID 반환"""
        return self.main_category.value


# 서브 카테고리 목록
SUB_CATEGORIES = [
    # 올바른 분리배출
    SubCategory(0, '페트병 라벨 제거', MainCategory.PROPER_DISPOSAL),
    SubCategory(1, '택배 상자 테이프/송장 제거', MainCategory.PROPER_DISPOSAL),
    SubCategory(2, '내용물이 비워진 우유갑/주스팩', MainCategory.PROPER_DISPOSAL),
    SubCategory(3, '깨끗한 스티로폼 박스', MainCategory.PROPER_DISPOSAL),

    # 다회용품 사용
    SubCategory(4, '카페/식당에서의 텀블러 사용', MainCategory.REUSABLE_ITEMS),
    SubCategory(5, '다회용기(용기내) 포장', MainCategory.REUSABLE_ITEMS),
    SubCategory(6, '장바구니 사용', MainCategory.REUSABLE_ITEMS),

    # 자원 절약 및 재활용
    SubCategory(7, '전자영수증 발급 화면', MainCategory.RESOURCE_SAVING),
    SubCategory(8, '사용하지 않는 플러그 뽑기', MainCategory.RESOURCE_SAVING),
]

# 빠른 조회를 위한 딕셔너리
_SUB_CATEGORY_MAP: Dict[int, SubCategory] = {sc.id: sc for sc in SUB_CATEGORIES}


def _get_main_category(category_id: int) -> Optional[MainCategory]:
    """메인 카테고리 ID로 MainCategory 반환 (내부 헬퍼)"""
    try:
        return MainCategory(category_id)
    except ValueError:
        return None


def _get_sub_category(sub_category_id: int) -> Optional[SubCategory]:
    """서브 카테고리 ID로 SubCategory 반환 (내부 헬퍼)"""
    return _SUB_CATEGORY_MAP.get(sub_category_id)


def _validate_category_pair(main_category_id: int, sub_category_id: int) -> tuple[bool, Optional[str]]:
    """
    메인 카테고리와 서브 카테고리의 유효성 및 관계 검증 (내부 헬퍼)

    Returns:
        (is_valid, error_message): 유효하면 (True, None), 무효하면 (False, 에러 메시지)
    """
    main_category = _get_main_category(main_category_id)
    if not main_category:
        return False, f"Invalid main category index: {main_category_id}"

    sub_category = _get_sub_category(sub_category_id)
    if not sub_category:
        return False, f"Invalid sub category index: {sub_category_id}"

    if sub_category.main_category_id != main_category_id:
        return False, f"Sub category {sub_category_id} does not belong to main category {main_category_id}"

    return True, None

# 이미지 검증 스키마
category_verification_schema = types.Schema(
    type="object",
    properties={
        "is_valid": types.Schema(type="boolean", description="Is the image appropriate for the selected category and subcategory?"),
        "confidence": types.Schema(type="number", description="Confidence level (0-1) of the verification"),
        "reason": types.Schema(type="string", description="Reason for the verification result"),
    },
    required=["is_valid", "confidence", "reason"],
)

# O/X 퀴즈 응답 스키마
quiz_ox_response_schema = types.Schema(
    type="object",
    properties={
        "question": types.Schema(type="string", description="The O/X quiz statement in Korean."),
        "answer": types.Schema(type="string", description="The correct answer, either 'O' or 'X'."),
        "explanation": types.Schema(type="string", description="A brief explanation in Korean."),
    },
    required=["question", "answer", "explanation"],
)


class VerificationService:
    """인증(이미지, 퀴즈, 소감문) 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        self.base_repo = BaseRepository()
        # 소감문 검증을 위한 모델 (필요시 초기화)
        self.similarity_model = None

    async def verify_image_by_category(
        self,
        image_bytes: bytes,
        main_category_index: int,
        sub_category_index: int
    ) -> str:
        """카테고리별 이미지 검증"""
        # 카테고리 유효성 및 관계 검증
        is_valid, error_message = _validate_category_pair(main_category_index, sub_category_index)
        if not is_valid:
            raise ValueError(error_message)

        # 서브 카테고리 정보 가져오기 (검증 완료했으므로 None이 아님)
        sub_category = _get_sub_category(sub_category_index)
        if not sub_category:  # 타입 체커를 위한 추가 검증
            raise ValueError(f"Sub category {sub_category_index} not found")

        main_category_name = sub_category.main_category.display_name
        sub_category_name = sub_category.name

        # 시스템 프롬프트 생성
        system_prompt = f"""
        You are an AI image verification specialist for "zeroro", an environmental app. Your task is to analyze a user-submitted image with extreme focus and strictness.

        **Action to Verify:**
        - **Main Category:** "{main_category_name}"
        - **Specific Action:** "{sub_category_name}"

        **Your Primary Objective:**
        Your one and only goal is to determine if the image provides **direct, undeniable proof** that the user performed the **"Specific Action"** listed above. All other observations are secondary. If the proof for the specific action is not present, the verification must fail, regardless of any other positive environmental activities shown in the image.

        **Evaluation Criteria & Thought Process:**
        1.  **Identify Core Evidence:** First, identify the essential objects and their state required to prove the "Specific Action". (e.g., for 'Removing a bottle label', the core evidence is a BOTTLE and a DETACHED LABEL).
        2.  **Scan for Core Evidence:** Does the image contain this core evidence? This is a simple yes/no check. If no, fail immediately.
        3.  **Assess State & Context:** If the evidence is present, is it in the correct state? (e.g., Is the label *fully* detached?).
        4.  **Check Authenticity:** Does this look like a genuine, user-taken photo?

        **Final Judgement:**
        - **Success (is_valid: true):** Only when there is clear and direct evidence of the **"Specific Action"**.
        - **Failure (is_valid: false):** In ALL other cases. For example, if the action is "Removing the label from a PET bottle" and the user uploads a picture of recycling 10 plastic bottles (a good deed, but not the specified action), you MUST return `false`.

        Provide your response ONLY in the specified JSON schema format. The 'reason' must be a concise explanation in **Korean**.
        """

        try:
            api_key = get_gemini_api_key()
            client = genai.Client(api_key=api_key)

            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/jpeg"
                    ),
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=category_verification_schema,
                    system_instruction=system_prompt
                ),
            )
            return response.text

        except Exception as e:
            raise Exception(f"이미지 검증 중 오류가 발생했습니다: {str(e)}")

    async def create_user_behavior(self, behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 행동 제안 생성"""
        created_behavior = await self.base_repo.create("suggest_behavior", behavior_data)
        if not created_behavior:
            raise HTTPException(status_code=500, detail="행동 제안 생성에 실패했습니다.")

        return {"behavior": created_behavior}

    async def create_ox_quiz(self) -> Dict[str, Any]:
        """O/X 퀴즈 생성"""
        system_prompt = """
        You are an AI quiz master for "zeroro", an environmental protection app.
        Your primary goal is to create a single, engaging True/False (O/X) style quiz question to educate users.

        Instructions:

        1.  Topic Selection: Autonomously select a surprising or lesser-known environmental fact. You can choose from a wide range of topics like recycling, energy conservation, food waste, biodiversity, fast fashion, or plastics. Your goal is to find an interesting fact that most people might not know.
        2.  Question Format: The "question" must be a declarative statement (a fact) in Korean that can be judged as either true ('O') or false ('X').
        3.  Language: The entire output (question, answer, explanation) MUST be in Korean.
        4.  Clarity & Tone: Keep the question and explanation concise and easy to understand for a general audience. The tone should be educational and engaging, making users feel like they've learned something new.
        """

        try:
            api_key = get_gemini_api_key()
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents="Generate one O/X quiz now.",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=quiz_ox_response_schema,
                    system_instruction=system_prompt
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            raise Exception(f"퀴즈 생성 중 오류가 발생했습니다: {str(e)}")

    async def verify_article_summary(
        self,
        summary: str,
        concepts: list[str],
        threshold: float = 0.5
    ) -> bool:
        """소감문 검증 (의미적 유사도 기반)"""
        if not summary or not concepts:
            return False

        # 모델 초기화 (lazy loading)
        if self.similarity_model is None:
            self.similarity_model = SentenceTransformer('jhgan/ko-sroberta-multitask')

        summary_embedding = self.similarity_model.encode(summary, convert_to_tensor=True)
        concept_embeddings = self.similarity_model.encode(concepts, convert_to_tensor=True)

        cosine_scores = util.cos_sim(summary_embedding, concept_embeddings)
        max_score = cosine_scores.max().item()

        print(f"DEBUG: Max similarity score is {max_score}")

        return max_score > threshold
