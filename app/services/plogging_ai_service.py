"""Plogging AI Service - AI 기반 플로깅 사진 검증"""
from typing import Dict, Any
from google import genai
from google.genai import types
import json
import base64
import httpx

from app.core.config import get_gemini_api_key
from app.schemas.plogging_schemas import AIVerificationResult, AIComparisonResult


# AI 검증 결과 스키마
plogging_verification_schema = types.Schema(
    type="object",
    properties={
        "is_valid": types.Schema(
            type="boolean",
            description="이 사진이 플로깅 활동(쓰레기 줍기)을 보여주는지 여부"
        ),
        "confidence": types.Schema(
            type="number",
            description="판단에 대한 신뢰도 (0.0 ~ 1.0)"
        ),
        "detected_items": types.Schema(
            type="array",
            items=types.Schema(type="string"),
            description="감지된 항목 목록 (예: 쓰레기, 쓰레기봉투, 집게 등)"
        ),
        "reason": types.Schema(
            type="string",
            description="검증 결과에 대한 한국어 설명"
        ),
    },
    required=["is_valid", "confidence", "detected_items", "reason"],
)


# 두 사진 비교 검증 스키마
plogging_comparison_schema = types.Schema(
    type="object",
    properties={
        "is_same_person": types.Schema(
            type="boolean",
            description="두 사진에 동일 인물이 있는지 여부"
        ),
        "trash_increased": types.Schema(
            type="boolean",
            description="쓰레기 양이 증가했는지 여부 (빡빡하지 않게 판단)"
        ),
        "confidence": types.Schema(
            type="number",
            description="판단에 대한 신뢰도 (0.0 ~ 1.0)"
        ),
        "reason": types.Schema(
            type="string",
            description="검증 결과에 대한 한국어 설명"
        ),
    },
    required=["is_same_person", "trash_increased", "confidence", "reason"],
)


PLOGGING_COMPARISON_PROMPT = """
You are an AI verification specialist for "Zeroro", an environmental plogging app.
Your task is to compare TWO images: an INITIAL photo (before plogging) and a CURRENT photo (during plogging).

**Your job is to verify:**
1. **Same Person Check**: Is it the same person in both photos?
   - Look for similar clothing, body type, accessories
   - Be lenient - partial visibility is OK if other cues match

2. **Trash Increase Check**: Has the amount of collected trash increased?
   - Compare the bag/container fullness between photos
   - ANY visible increase counts as success
   - Be encouraging - even small increases are valid
   - The initial photo shows an empty/near-empty container
   - The current photo should show more trash in the container

**Confidence Guidelines:**
- 0.8-1.0: Clear match and visible trash increase
- 0.6-0.8: Reasonable match, some ambiguity but likely valid
- Below 0.6: Cannot verify with confidence

**Important:**
- Be encouraging but honest
- The 'reason' must be in Korean
- If verification fails, provide constructive feedback
- Remember: this is to encourage environmental activity, not to catch cheaters

The FIRST image is the INITIAL photo (before starting).
The SECOND image is the CURRENT photo (during plogging).
"""


PLOGGING_VERIFICATION_PROMPT = """
You are an AI verification specialist for "Zeroro", an environmental plogging app.
Your task is to verify if the user-submitted image shows evidence of active plogging (picking up litter while walking/jogging).

**Verification Criteria:**

1. **Primary Evidence (at least one required):**
   - Visible trash/litter being held or collected
   - Trash bags with collected items
   - Hands holding/picking up litter
   - Plogging equipment (pickers, gloves) with collected trash

2. **Supporting Evidence (helpful but not required):**
   - Outdoor environment (park, street, trail)
   - Person actively engaged in collection activity

3. **Rejection Cases:**
   - Indoor photos without collected trash
   - Empty trash bags or equipment without evidence of collection
   - Unrelated images (food, selfies without context, etc.)
   - Photos that are too blurry or dark to verify

**Confidence Guidelines:**
- 0.9-1.0: Clear evidence of plogging with visible collected trash
- 0.7-0.9: Good evidence but some ambiguity
- 0.5-0.7: Moderate evidence, some elements present
- Below 0.5: Insufficient evidence

**Important:**
- Be encouraging but honest - if the evidence is unclear, provide constructive feedback
- The 'reason' must be in Korean and be helpful for the user to understand the result
- If rejected, suggest what kind of photo would be accepted

Provide your response ONLY in the specified JSON schema format.
"""


class PloggingAIService:
    """플로깅 AI 검증 서비스"""

    VERIFICATION_THRESHOLD = 0.6  # 60% 이상이면 통과

    def __init__(self):
        self.api_key = get_gemini_api_key()

    async def verify_plogging_image(
        self,
        image_url: str
    ) -> AIVerificationResult:
        """
        플로깅 사진 검증

        Parameters:
        - image_url: 검증할 이미지 URL

        Returns:
        - AIVerificationResult: 검증 결과
        """
        try:
            # 이미지 다운로드
            image_bytes = await self._download_image(image_url)

            # Gemini API 호출
            client = genai.Client(api_key=self.api_key)

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/jpeg"
                    ),
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=plogging_verification_schema,
                    system_instruction=PLOGGING_VERIFICATION_PROMPT
                ),
            )

            # 응답 파싱
            result = json.loads(response.text)

            return AIVerificationResult(
                is_valid=result.get("is_valid", False),
                confidence=result.get("confidence", 0.0),
                detected_items=result.get("detected_items", []),
                reason=result.get("reason", "검증 결과를 확인할 수 없습니다.")
            )

        except Exception as e:
            # 에러 발생 시 실패로 처리
            return AIVerificationResult(
                is_valid=False,
                confidence=0.0,
                detected_items=[],
                reason=f"검증 중 오류가 발생했습니다: {str(e)}"
            )

    async def verify_plogging_image_bytes(
        self,
        image_bytes: bytes
    ) -> AIVerificationResult:
        """
        플로깅 사진 검증 (바이트 직접 전달)

        Parameters:
        - image_bytes: 이미지 바이트 데이터

        Returns:
        - AIVerificationResult: 검증 결과
        """
        try:
            client = genai.Client(api_key=self.api_key)

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/jpeg"
                    ),
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=plogging_verification_schema,
                    system_instruction=PLOGGING_VERIFICATION_PROMPT
                ),
            )

            result = json.loads(response.text)

            return AIVerificationResult(
                is_valid=result.get("is_valid", False),
                confidence=result.get("confidence", 0.0),
                detected_items=result.get("detected_items", []),
                reason=result.get("reason", "검증 결과를 확인할 수 없습니다.")
            )

        except Exception as e:
            return AIVerificationResult(
                is_valid=False,
                confidence=0.0,
                detected_items=[],
                reason=f"검증 중 오류가 발생했습니다: {str(e)}"
            )

    def is_verification_passed(self, result: AIVerificationResult) -> bool:
        """
        검증 통과 여부 판단

        Parameters:
        - result: AI 검증 결과

        Returns:
        - bool: 통과 여부 (is_valid=True AND confidence >= THRESHOLD)
        """
        return result.is_valid and result.confidence >= self.VERIFICATION_THRESHOLD

    async def _download_image(self, url: str) -> bytes:
        """URL에서 이미지 다운로드"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.content

    async def compare_plogging_images(
        self,
        initial_image_url: str,
        current_image_url: str
    ) -> AIComparisonResult:
        """
        초기 사진과 현재 사진 비교 검증

        Parameters:
        - initial_image_url: 플로깅 시작 전 촬영한 초기 사진 URL
        - current_image_url: 인증 시 촬영한 현재 사진 URL

        Returns:
        - AIComparisonResult: 비교 검증 결과
        """
        try:
            # 두 이미지 다운로드
            initial_bytes = await self._download_image(initial_image_url)
            current_bytes = await self._download_image(current_image_url)

            # Gemini API 호출 (두 이미지 전달)
            client = genai.Client(api_key=self.api_key)

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    types.Part.from_bytes(
                        data=initial_bytes,
                        mime_type="image/jpeg"
                    ),
                    types.Part.from_bytes(
                        data=current_bytes,
                        mime_type="image/jpeg"
                    ),
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=plogging_comparison_schema,
                    system_instruction=PLOGGING_COMPARISON_PROMPT
                ),
            )

            result = json.loads(response.text)

            return AIComparisonResult(
                is_same_person=result.get("is_same_person", False),
                trash_increased=result.get("trash_increased", False),
                confidence=result.get("confidence", 0.0),
                reason=result.get("reason", "검증 결과를 확인할 수 없습니다.")
            )

        except Exception as e:
            return AIComparisonResult(
                is_same_person=False,
                trash_increased=False,
                confidence=0.0,
                reason=f"검증 중 오류가 발생했습니다: {str(e)}"
            )

    def is_comparison_passed(self, result: AIComparisonResult) -> bool:
        """
        비교 검증 통과 여부 판단

        Parameters:
        - result: AI 비교 검증 결과

        Returns:
        - bool: 통과 여부 (동일 인물 AND 쓰레기 증가 AND confidence >= THRESHOLD)
        """
        return (
            result.is_same_person and
            result.trash_increased and
            result.confidence >= self.VERIFICATION_THRESHOLD
        )
