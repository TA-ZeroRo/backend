from fastapi import APIRouter
from uuid import UUID
from app.services.user_service import UserService
from app.schemas.user_schemas import UserCreate, UserUpdate, UserResponse

router = APIRouter()
user_service = UserService()

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreate):
    """
    새로운 사용자를 생성합니다.
    """
    return await user_service.create_user(user_data)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID):
    """
    특정 사용자의 정보를 가져옵니다.
    """
    return await user_service.get_user_by_id(user_id)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: UUID, user_data: UserUpdate):
    """
    사용자 정보를 수정합니다.
    """
    return await user_service.update_user(user_id, user_data)

@router.delete("/{user_id}")
async def delete_user(user_id: UUID):
    """
    사용자를 삭제합니다.
    """
    return await user_service.delete_user(user_id)

@router.post("/{user_id}/personality/gacha")
async def gacha_personality(user_id: UUID):
    """
    성격 뽑기를 진행합니다.
    300포인트마다 1번 뽑을 수 있으며, 포인트는 차감되지 않습니다.
    랜덤으로 성격을 뽑아서 반환합니다.
    """
    return await user_service.gacha_personality(user_id)