"""Recruiting Chat API Endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from app.services.recruiting_chat_service import RecruitingChatService
from app.schemas.recruiting_chat_schemas import (
    RecruitingPostCreate,
    RecruitingPostUpdate,
    RecruitingPostResponse,
    RecruitingPostDelete,
    ChatMessageSend,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatRoomResponse,
    JoinRecruitingRequest,
    KickParticipantRequest,
    LeaveRecruitingRequest
)

router = APIRouter()
recruiting_service = RecruitingChatService()

# ------------------------------
# --- START: 리크루팅 게시글 API ---
# ------------------------------
@router.get("/posts", response_model=List[RecruitingPostResponse])
async def get_recruiting_posts(
    offset: int,
    campaign_id: Optional[int] = None,
    region: Optional[str] = None,
    participation_status: Optional[str] = Query(None, description="all, participating, recruiting"),
    user_id: Optional[str] = None
):
    """
    리크루팅 게시글 목록을 가져옵니다.

    Parameters:
    - offset (int): 페이지네이션을 위한 시작 인덱스 (필수)
    - campaign_id (int, optional): 특정 캠페인의 리크루팅만 필터링
    - region (str, optional): 특정 지역의 리크루팅만 필터링
    - participation_status (str, optional): all(전체), participating(참여중), recruiting(모집중)
    - user_id (str, optional): 현재 사용자 ID (참여 여부 확인용)
    """
    return await recruiting_service.get_recruiting_posts(
        offset=offset,
        campaign_id=campaign_id,
        region=region,
        participation_status=participation_status,
        user_id=user_id
    )


@router.get("/posts/{post_id}", response_model=RecruitingPostResponse)
async def get_single_recruiting_post(post_id: int, user_id: Optional[str] = None):
    """
    특정 리크루팅 게시글의 상세 정보를 가져옵니다.

    Parameters:
    - post_id (int): 게시글 ID
    - user_id (str, optional): 현재 사용자 ID (참여 여부 확인용)
    """
    return await recruiting_service.get_single_recruiting_post(post_id, user_id)


@router.post("/posts", response_model=RecruitingPostResponse, status_code=201)
async def create_recruiting_post(post_data: RecruitingPostCreate):
    """
    새로운 리크루팅 게시글을 생성합니다.
    게시글 생성 시 채팅방이 자동으로 생성되며, 작성자가 첫 참여자가 됩니다.
    """
    return await recruiting_service.create_recruiting_post(post_data)


@router.put("/posts/{post_id}", response_model=RecruitingPostResponse)
async def update_recruiting_post(post_id: int, post_data: RecruitingPostUpdate):
    """
    리크루팅 게시글을 수정합니다.
    작성자만 수정할 수 있습니다.
    """
    return await recruiting_service.update_recruiting_post(post_id, post_data)


@router.delete("/posts/{post_id}")
async def delete_recruiting_post(post_id: int, delete_data: RecruitingPostDelete):
    """
    리크루팅 게시글을 삭제합니다.
    작성자만 삭제할 수 있습니다.
    """
    return await recruiting_service.delete_recruiting_post(post_id, delete_data)


@router.post("/posts/{post_id}/join", response_model=RecruitingPostResponse)
async def join_recruiting(post_id: int, join_data: JoinRecruitingRequest):
    """
    리크루팅에 참여합니다.
    참여 시 채팅방에 자동으로 추가되며, 현재 참여 인원이 증가합니다.

    Parameters:
    - post_id (int): 참여할 리크루팅 게시글 ID
    - join_data (JoinRecruitingRequest): 참여 요청 데이터 (user_id 포함)
    """
    return await recruiting_service.join_recruiting(post_id, join_data)


@router.delete("/posts/{post_id}/kick")
async def kick_participant(post_id: int, kick_data: KickParticipantRequest):
    """
    리크루팅 참여자를 강퇴합니다.
    주최자만 강퇴할 수 있습니다.

    Parameters:
    - post_id (int): 리크루팅 게시글 ID
    - kick_data (KickParticipantRequest): 강퇴 요청 데이터 (host_user_id, target_user_id 포함)
    """
    return await recruiting_service.kick_participant(post_id, kick_data)


@router.delete("/posts/{post_id}/leave")
async def leave_recruiting(post_id: int, leave_data: LeaveRecruitingRequest):
    """
    리크루팅에서 나갑니다.
    참여자만 나갈 수 있으며, 주최자는 나갈 수 없습니다.

    Parameters:
    - post_id (int): 리크루팅 게시글 ID
    - leave_data (LeaveRecruitingRequest): 나가기 요청 데이터 (user_id 포함)
    """
    return await recruiting_service.leave_recruiting(post_id, leave_data)

# ----------------------------
# --- END: 리크루팅 게시글 API ---
# ----------------------------


# --------------------------
# --- START: 채팅 메시지 API ---
# --------------------------
@router.get("/rooms/{room_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    room_id: int,
    user_id: str,
    offset: int = 0,
    limit: int = Query(50, le=100, description="최대 100개까지 조회 가능")
):
    """
    채팅방의 메시지 목록을 가져옵니다.
    채팅방 참여자만 조회할 수 있습니다.

    Parameters:
    - room_id (int): 채팅방 ID
    - user_id (str): 현재 사용자 ID (권한 검증용)
    - offset (int, optional): 페이지네이션 시작 인덱스 (기본값: 0)
    - limit (int, optional): 조회할 메시지 개수 (기본값: 50, 최대: 100)
    """
    return await recruiting_service.get_chat_messages(room_id, user_id, offset, limit)


@router.post("/rooms/{room_id}/messages", response_model=ChatMessageResponse, status_code=201)
async def send_chat_message(room_id: int, message_data: ChatMessageSend):
    """
    채팅방에 메시지를 전송합니다.
    채팅방 참여자만 메시지를 보낼 수 있습니다.

    Parameters:
    - room_id (int): 채팅방 ID
    - message_data (ChatMessageSend): 메시지 데이터 (user_id, message 포함)
    """
    # ChatMessageSend -> ChatMessageCreate로 변환
    create_data = ChatMessageCreate(
        user_id=message_data.user_id,
        message=message_data.message,
        chat_room_id=room_id
    )
    return await recruiting_service.send_chat_message(create_data)


@router.get("/rooms/{room_id}/participants")
async def get_chat_room_participants(room_id: int, user_id: str):
    """
    채팅방의 참여자 목록을 가져옵니다.
    채팅방 참여자만 조회할 수 있습니다.

    Parameters:
    - room_id (int): 채팅방 ID
    - user_id (str): 현재 사용자 ID (권한 검증용)
    """
    return await recruiting_service.get_chat_room_participants(room_id, user_id)

# ------------------------
# --- END: 채팅 메시지 API ---
# ------------------------
