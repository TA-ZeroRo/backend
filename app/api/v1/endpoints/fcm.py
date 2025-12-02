"""FCM Token API Endpoints"""
from fastapi import APIRouter, HTTPException
from app.services.fcm_service import FcmService
from app.schemas.fcm_schemas import FcmTokenRegister, FcmTokenDelete

router = APIRouter()
fcm_service = FcmService()


@router.post("/token", response_model=dict)
async def register_fcm_token(token_data: FcmTokenRegister):
    """
    FCM 토큰 등록

    앱 시작 시 또는 토큰 갱신 시 호출합니다.
    이미 등록된 토큰이면 업데이트합니다.
    """
    result = await fcm_service.register_token(
        user_id=str(token_data.user_id),
        fcm_token=token_data.fcm_token,
        platform=token_data.platform
    )

    if not result:
        raise HTTPException(status_code=500, detail="FCM 토큰 등록에 실패했습니다.")

    return {"message": "FCM 토큰이 등록되었습니다.", "data": result}


@router.delete("/token", response_model=dict)
async def delete_fcm_token(token_data: FcmTokenDelete):
    """
    FCM 토큰 삭제

    로그아웃 시 호출합니다.
    """
    success = await fcm_service.delete_token(
        user_id=str(token_data.user_id),
        fcm_token=token_data.fcm_token
    )

    if not success:
        raise HTTPException(status_code=500, detail="FCM 토큰 삭제에 실패했습니다.")

    return {"message": "FCM 토큰이 삭제되었습니다."}
