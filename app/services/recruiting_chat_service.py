"""Recruiting Chat Service - 리크루팅 및 채팅 관련 비즈니스 로직"""
from fastapi import HTTPException
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import date
from app.repository.recruiting_chat_repository import RecruitingChatRepository
from app.services.fcm_service import FcmService
from app.schemas.recruiting_chat_schemas import (
    RecruitingPostCreate,
    RecruitingPostUpdate,
    RecruitingPostDelete,
    ChatMessageCreate,
    JoinRecruitingRequest,
    KickParticipantRequest
)
from app.schemas.fcm_schemas import ChatPushNotification


class RecruitingChatService:
    """리크루팅 및 채팅 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        self.recruiting_repo = RecruitingChatRepository()
        self.fcm_service = FcmService()

    # ===== RecruitingPost 관련 메서드 =====
    async def get_recruiting_posts(
        self,
        offset: int,
        campaign_id: Optional[int] = None,
        region: Optional[str] = None,
        participation_status: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """리크루팅 게시글 목록 조회 (페이지네이션 및 필터링)"""
        if offset < 0:
            raise HTTPException(status_code=400, detail="offset은 0 이상이어야 합니다.")

        limit = 10

        # participation_status 필터링 처리
        if participation_status == "participating":
            # 참여 중인 게시글만 조회
            if not user_id:
                raise HTTPException(status_code=400, detail="참여 중인 게시글을 조회하려면 user_id가 필요합니다.")
            posts = await self.recruiting_repo.get_user_participating_posts(user_id, offset, limit)
        elif participation_status == "recruiting":
            # 모집 중인 게시글만 조회
            posts = await self.recruiting_repo.get_recruiting_posts_paginated(
                offset=offset,
                limit=limit,
                campaign_id=campaign_id,
                region=region,
                is_recruiting=True,
                user_id=user_id
            )
        else:
            # 전체 게시글 조회
            posts = await self.recruiting_repo.get_recruiting_posts_paginated(
                offset=offset,
                limit=limit,
                campaign_id=campaign_id,
                region=region,
                user_id=user_id
            )

        return posts

    async def get_single_recruiting_post(self, post_id: int, user_id: Optional[str] = None) -> Dict[str, Any]:
        """특정 리크루팅 게시글 상세 정보 조회"""
        post = await self.recruiting_repo.get_recruiting_post_by_id(post_id, user_id)
        if not post:
            raise HTTPException(status_code=404, detail="해당 리크루팅 게시글을 찾을 수 없습니다.")

        return post

    async def create_recruiting_post(self, post_data: RecruitingPostCreate) -> Dict[str, Any]:
        """새로운 리크루팅 게시글 생성"""
        # 날짜 유효성 검증
        if post_data.end_date and post_data.start_date > post_data.end_date:
            raise HTTPException(status_code=400, detail="종료 날짜는 시작 날짜 이후여야 합니다.")

        # 연령 유효성 검증
        if post_data.min_age > 0 and post_data.max_age > 0:
            if post_data.min_age > post_data.max_age:
                raise HTTPException(status_code=400, detail="최소 연령은 최대 연령보다 작거나 같아야 합니다.")

        # 게시글 데이터 준비
        insert_data = {
            "user_id": str(post_data.user_id),
            "campaign_id": post_data.campaign_id,
            "title": post_data.title,
            "region": post_data.region,
            "city": post_data.city,
            "capacity": post_data.capacity,
            "current_members": 1,  # 작성자가 첫 참여자
            "start_date": post_data.start_date.isoformat(),
            "min_age": post_data.min_age,
            "max_age": post_data.max_age,
            "is_recruiting": True
        }

        # 선택적 필드 추가
        if post_data.end_date:
            insert_data["end_date"] = post_data.end_date.isoformat()

        created_post = await self.recruiting_repo.create_recruiting_post(insert_data)
        if not created_post:
            raise HTTPException(status_code=500, detail="리크루팅 게시글 생성에 실패했습니다.")

        # 채팅방 자동 생성 및 작성자 자동 참여
        chat_room = await self.recruiting_repo.create_chat_room({
            "recruiting_post_id": created_post["id"]
        })

        if chat_room:
            # 작성자를 채팅방 참여자로 추가
            await self.recruiting_repo.add_participant(chat_room["id"], str(post_data.user_id))
            created_post["chat_room_id"] = chat_room["id"]
            created_post["is_participating"] = True

        return created_post

    async def update_recruiting_post(self, post_id: int, post_data: RecruitingPostUpdate) -> Dict[str, Any]:
        """리크루팅 게시글 업데이트 (권한 검증 포함)"""
        # 작성자 권한 검증
        post = await self.recruiting_repo.get_recruiting_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="해당 리크루팅 게시글을 찾을 수 없습니다.")

        if str(post.get("user_id")) != str(post_data.user_id):
            raise HTTPException(status_code=403, detail="게시글을 수정할 권한이 없습니다.")

        # 업데이트할 데이터만 추출 (None이 아닌 값만, user_id 제외)
        update_data = {k: v for k, v in post_data.model_dump(exclude={"user_id"}).items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="업데이트할 데이터가 없습니다.")

        # 날짜 변환 (date 객체를 문자열로)
        if "start_date" in update_data:
            update_data["start_date"] = update_data["start_date"].isoformat()
        if "end_date" in update_data and update_data["end_date"]:
            update_data["end_date"] = update_data["end_date"].isoformat()

        # 날짜 유효성 검증
        if "start_date" in update_data and "end_date" in update_data:
            if update_data["end_date"] and update_data["start_date"] > update_data["end_date"]:
                raise HTTPException(status_code=400, detail="종료 날짜는 시작 날짜 이후여야 합니다.")

        # 연령 유효성 검증
        min_age = update_data.get("min_age", post.get("min_age", 0))
        max_age = update_data.get("max_age", post.get("max_age", 0))
        if min_age > 0 and max_age > 0:
            if min_age > max_age:
                raise HTTPException(status_code=400, detail="최소 연령은 최대 연령보다 작거나 같아야 합니다.")

        # 정원 변경 시 현재 인원보다 작은지 확인
        if "capacity" in update_data:
            if update_data["capacity"] < post.get("current_members", 1):
                raise HTTPException(
                    status_code=400,
                    detail=f"정원은 현재 참여 인원({post['current_members']}명)보다 작을 수 없습니다."
                )

        updated_post = await self.recruiting_repo.update_recruiting_post(
            post_id, update_data, str(post_data.user_id)
        )
        if not updated_post:
            raise HTTPException(status_code=500, detail="게시글 수정에 실패했습니다.")

        return updated_post

    async def delete_recruiting_post(self, post_id: int, delete_data: RecruitingPostDelete) -> Dict[str, str]:
        """리크루팅 게시글 삭제 (권한 검증 포함)"""
        # 작성자 권한 검증
        post = await self.recruiting_repo.get_recruiting_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="해당 리크루팅 게시글을 찾을 수 없습니다.")

        if str(post.get("user_id")) != str(delete_data.user_id):
            raise HTTPException(status_code=403, detail="게시글을 삭제할 권한이 없습니다.")

        success = await self.recruiting_repo.delete_recruiting_post(post_id)
        if not success:
            raise HTTPException(status_code=500, detail="게시글 삭제에 실패했습니다.")

        return {"message": "게시글이 성공적으로 삭제되었습니다."}

    async def join_recruiting(self, post_id: int, join_data: JoinRecruitingRequest) -> Dict[str, Any]:
        """리크루팅 참여하기 (채팅방 참여)"""
        # 게시글 존재 확인
        post = await self.recruiting_repo.get_recruiting_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="해당 리크루팅 게시글을 찾을 수 없습니다.")

        # 모집 중인지 확인
        if not post.get("is_recruiting", False):
            raise HTTPException(status_code=400, detail="현재 모집이 마감된 게시글입니다.")

        # 정원 확인
        if post["current_members"] >= post["capacity"]:
            raise HTTPException(status_code=400, detail="정원이 가득 찼습니다.")

        # 채팅방 조회 또는 생성
        chat_room = await self.recruiting_repo.get_chat_room_by_recruiting_post_id(post_id)
        if not chat_room:
            chat_room = await self.recruiting_repo.create_chat_room({
                "recruiting_post_id": post_id
            })
            if not chat_room:
                raise HTTPException(status_code=500, detail="채팅방 생성에 실패했습니다.")

        # 이미 참여 중인지 확인
        is_participant = await self.recruiting_repo.is_user_participant(
            chat_room["id"], str(join_data.user_id)
        )
        if is_participant:
            raise HTTPException(status_code=400, detail="이미 참여 중인 리크루팅입니다.")

        # 참여자 추가
        success = await self.recruiting_repo.add_participant(chat_room["id"], str(join_data.user_id))
        if not success:
            raise HTTPException(status_code=500, detail="참여에 실패했습니다.")

        # 현재 참여 인원 증가
        await self.recruiting_repo.increment_current_members(post_id)

        # 업데이트된 게시글 반환
        updated_post = await self.recruiting_repo.get_recruiting_post_by_id(post_id, str(join_data.user_id))
        return updated_post

    # ===== ChatMessage 관련 메서드 =====
    async def get_chat_messages(
        self,
        room_id: int,
        user_id: str,
        offset: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """채팅방 메시지 목록 조회 (권한 검증 포함)"""
        # 채팅방 존재 확인
        chat_room = await self.recruiting_repo.get_chat_room_by_id(room_id)
        if not chat_room:
            raise HTTPException(status_code=404, detail="해당 채팅방을 찾을 수 없습니다.")

        # 참여자 권한 검증
        is_participant = await self.recruiting_repo.is_user_participant(room_id, user_id)
        if not is_participant:
            raise HTTPException(status_code=403, detail="채팅방에 접근할 권한이 없습니다.")

        # 메시지 조회
        messages = await self.recruiting_repo.get_messages_by_room_id(room_id, offset, limit)
        return messages

    async def send_chat_message(self, message_data: ChatMessageCreate) -> Dict[str, Any]:
        """채팅 메시지 전송 (권한 검증 포함)"""
        # 채팅방 존재 확인
        chat_room = await self.recruiting_repo.get_chat_room_by_id(message_data.chat_room_id)
        if not chat_room:
            raise HTTPException(status_code=404, detail="해당 채팅방을 찾을 수 없습니다.")

        # 참여자 권한 검증
        is_participant = await self.recruiting_repo.is_user_participant(
            message_data.chat_room_id, str(message_data.user_id)
        )
        if not is_participant:
            raise HTTPException(status_code=403, detail="채팅방에 메시지를 보낼 권한이 없습니다.")

        # 메시지 데이터 준비
        insert_data = {
            "chat_room_id": message_data.chat_room_id,
            "user_id": str(message_data.user_id),
            "message": message_data.message
        }

        created_message = await self.recruiting_repo.create_message(insert_data)
        if not created_message:
            raise HTTPException(status_code=500, detail="메시지 전송에 실패했습니다.")

        # 푸시 알림 발송 (비동기로 처리, 실패해도 메시지 전송은 성공)
        try:
            await self._send_chat_push_notification(
                chat_room_id=message_data.chat_room_id,
                sender_id=str(message_data.user_id),
                message=message_data.message,
                created_message=created_message
            )
        except Exception as e:
            # 푸시 알림 실패는 로그만 남기고 메시지 전송은 성공 처리
            print(f"Error sending push notification: {e}")

        return created_message

    async def _send_chat_push_notification(
        self,
        chat_room_id: int,
        sender_id: str,
        message: str,
        created_message: Dict[str, Any]
    ) -> None:
        """채팅 메시지 푸시 알림 발송 (내부 메서드)"""
        # 채팅방 참여자 목록 조회
        participants = await self.recruiting_repo.get_participants_by_room_id(chat_room_id)

        # 발신자를 제외한 참여자 ID 목록
        recipient_user_ids = [
            p["user_id"] for p in participants
            if p["user_id"] != sender_id
        ]

        if not recipient_user_ids:
            return

        # 발신자 정보 추출
        sender_profile = created_message.get("profiles", {})
        sender_name = sender_profile.get("username", "알 수 없는 사용자") if sender_profile else "알 수 없는 사용자"

        # 채팅방의 리크루팅 게시글 정보 조회
        chat_room = await self.recruiting_repo.get_chat_room_by_id(chat_room_id)
        recruiting_post_id = chat_room.get("recruiting_post_id") if chat_room else None
        recruiting_title = None

        if recruiting_post_id:
            post = await self.recruiting_repo.get_recruiting_post_by_id(recruiting_post_id)
            if post:
                recruiting_title = post.get("title")

        # 푸시 알림 데이터 생성
        notification_data = ChatPushNotification(
            chat_room_id=chat_room_id,
            sender_id=sender_id,
            sender_name=sender_name,
            message=message,
            recruiting_post_id=recruiting_post_id,
            recruiting_title=recruiting_title
        )

        # FCM 발송
        await self.fcm_service.send_chat_notification(
            notification_data=notification_data,
            recipient_user_ids=recipient_user_ids
        )

    async def get_chat_room_participants(self, room_id: int, user_id: str) -> List[Dict[str, Any]]:
        """채팅방 참여자 목록 조회 (권한 검증 포함)"""
        # 채팅방 존재 확인
        chat_room = await self.recruiting_repo.get_chat_room_by_id(room_id)
        if not chat_room:
            raise HTTPException(status_code=404, detail="해당 채팅방을 찾을 수 없습니다.")

        # 참여자 권한 검증
        is_participant = await self.recruiting_repo.is_user_participant(room_id, user_id)
        if not is_participant:
            raise HTTPException(status_code=403, detail="채팅방에 접근할 권한이 없습니다.")

        # 참여자 목록 조회
        participants = await self.recruiting_repo.get_participants_by_room_id(room_id)
        return participants

    async def kick_participant(self, post_id: int, kick_data: KickParticipantRequest) -> Dict[str, str]:
        """참여자 강퇴 (주최자만 가능)"""
        # 게시글 존재 확인
        post = await self.recruiting_repo.get_recruiting_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="해당 리크루팅 게시글을 찾을 수 없습니다.")

        # 주최자 권한 검증
        if str(post.get("user_id")) != str(kick_data.host_user_id):
            raise HTTPException(status_code=403, detail="참여자를 강퇴할 권한이 없습니다.")

        # 자기 자신 강퇴 방지
        if str(kick_data.host_user_id) == str(kick_data.target_user_id):
            raise HTTPException(status_code=400, detail="자기 자신을 강퇴할 수 없습니다.")

        # 채팅방 조회
        chat_room = await self.recruiting_repo.get_chat_room_by_recruiting_post_id(post_id)
        if not chat_room:
            raise HTTPException(status_code=404, detail="해당 채팅방을 찾을 수 없습니다.")

        # 대상이 참여자인지 확인
        is_participant = await self.recruiting_repo.is_user_participant(
            chat_room["id"], str(kick_data.target_user_id)
        )
        if not is_participant:
            raise HTTPException(status_code=400, detail="해당 사용자는 참여자가 아닙니다.")

        # 참여자 제거
        success = await self.recruiting_repo.remove_participant(
            chat_room["id"], str(kick_data.target_user_id)
        )
        if not success:
            raise HTTPException(status_code=500, detail="강퇴에 실패했습니다.")

        # 현재 참여 인원 감소
        await self.recruiting_repo.decrement_current_members(post_id)

        return {"message": "참여자가 성공적으로 강퇴되었습니다."}
