from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from app.services.verification_service import VerificationService

router = APIRouter()
verification_service = VerificationService()


# ===== 위치 검증 요청 스키마 =====
class LocationVerificationRequest(BaseModel):
    """위치 검증 요청"""
    campaign_id: int
    latitude: float
    longitude: float

# @router.post("/image")
# async def verify_image(image_data: dict):
#     """
#     이미지 업로드를 검증합니다.
#     """
#     try:
#         result = await verify_image_upload(image_data)
#         return {"result": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@router.post("/image")
async def verify_image_by_category_endpoint(
    image: UploadFile = File(...),
    main_category_index: int = Form(...),
    sub_category_index: int = Form(...)
):
    """
    프론트엔드에서 업로드한 이미지와 카테고리 인덱스를 기반으로 이미지를 검증합니다.
    """
    try:
        # 이미지 파일 검증
        if not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="유효한 이미지 파일이 아닙니다. (지원 형식: JPEG, PNG)"
            )
            
        # 이미지 크기 제한 (예: 10MB)
        MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
        image_data = await image.read()
        if len(image_data) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="이미지 크기가 너무 큽니다. 최대 10MB까지 허용됩니다."
            )
            
        # 타입 검증
        if not isinstance(main_category_index, int):
            raise HTTPException(status_code=400, detail="main_category_index는 정수여야 합니다.")
        
        if not isinstance(sub_category_index, int):
            raise HTTPException(status_code=400, detail="sub_category_index는 정수여야 합니다.")
        
        # 이미지 검증 서비스 호출
        result = await verification_service.verify_image_by_category(
            image_bytes=image_data,
            main_category_index=main_category_index,
            sub_category_index=sub_category_index
        )
        
        return {"result": result}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/behavior")
async def create_behavior(verification_behavior: dict):
    """
    이미지 인증 행동을 추가 요청합니다.
    """
    try:
        result = await verification_service.create_user_behavior(verification_behavior)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quiz")
async def create_quiz():
    """
    O/X 퀴즈를 생성합니다.
    """
    try:
        result = await verification_service.create_ox_quiz()
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        
# 기사 인증 API -> 추후 추가 예정
# @router.post("/summary")
# async def verify_article_summary(article_id: int, user_summary: str):
#     """
#     사용자가 제출한 소감문을 검증합니다.
#     """
#     try:
#         # 1. DB에서 article_id에 해당하는 글의 핵심 개념을 가져옵니다.
#         article_info = get_article_with_concepts(article_id)
#         if not article_info:
#             raise HTTPException(status_code=404, detail="Article not found")
        
#         key_concepts = article_info.get("key_concepts", [])
        
#         # 2. 소감문의 길이가 너무 짧은 경우 예외 처리
#         if len(user_summary) < 10:
#             raise HTTPException(status_code=400, detail="Summary is too short. Please write more sincerely.")

#         # 3. 검증 로직 함수 호출
#         is_verified = verify_summary(user_summary, key_concepts)

#         if not is_verified:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Verification failed. Your summary does not seem to be related to the article's content."
#             )

#         # 4. 인증 성공 시 포인트 지급 및 성공 응답 반환
#         points_earned = 50  # 예시 포인트
        
#         return {
#             "message": "Verification successful!",
#             "is_verified": True,
#             "points_earned": points_earned
#         }
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.post("/location")
async def verify_location(request: LocationVerificationRequest):
    """
    오프라인 캠페인의 위치 검증

    Request Body:
    - campaign_id: 캠페인 ID
    - latitude: 사용자 현재 위도
    - longitude: 사용자 현재 경도

    Response:
    - is_valid: 검증 성공 여부
    - reason: 검증 결과 메시지
    - distance: 캠페인 장소와의 거리 (미터)
    - verified_at: 검증 시간
    - location_address: 캠페인 장소 주소
    """
    try:
        # 위치 검증 수행
        result = await verification_service.verify_offline_campaign_location(
            campaign_id=request.campaign_id,
            user_lat=request.latitude,
            user_lng=request.longitude
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"위치 검증 중 오류가 발생했습니다: {str(e)}")
