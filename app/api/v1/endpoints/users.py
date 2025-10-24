from fastapi import APIRouter, HTTPException
from uuid import UUID
from app.services.user_service import UserService
from app.schemas.user_schemas import UserCreate, UserUpdate

router = APIRouter()
user_service = UserService()

@router.post("/")
async def create_user(user_data: UserCreate):
    """
    새로운 사용자를 생성합니다.
    """
    try:
        return await user_service.create_user(user_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}")
async def get_user(user_id: UUID):
    """
    특정 사용자의 정보를 가져옵니다.
    """
    try:
        return await user_service.get_user_by_id(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}")
async def update_user(user_id: UUID, user_data: UserUpdate):
    """
    사용자 정보를 수정합니다.
    """
    try:
        return await user_service.update_user(user_id, user_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(user_id: UUID):
    """
    사용자를 삭제합니다.
    """
    try:
        return await user_service.delete_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))