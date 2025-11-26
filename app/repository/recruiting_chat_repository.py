"""Recruiting Chat Repository"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from app.repository.base_repository import BaseRepository


class RecruitingChatRepository(BaseRepository):
    """리크루팅 및 채팅 관련 데이터베이스 작업을 처리하는 Repository"""

    RECRUITING_POST_TABLE = "recruiting_posts"
    CHAT_ROOM_TABLE = "recruiting_chat_rooms"
    CHAT_MESSAGE_TABLE = "recruiting_chat_messages"
    PARTICIPANT_TABLE = "recruiting_chat_room_participants"

    # ===== RecruitingPost 관련 메서드 =====
    async def get_recruiting_post_by_id(self, post_id: int, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """리크루팅 게시글 ID로 조회 (프로필 정보 포함)"""
        response = (
            self.supabase
            .table(self.RECRUITING_POST_TABLE)
            .select("*, profiles(user_img, username)")
            .eq("id", post_id)
            .execute()
        )

        if not response.data or len(response.data) == 0:
            return None

        post = response.data[0]

        # 채팅방 ID 조회
        chat_room = await self.get_chat_room_by_recruiting_post_id(post_id)
        if chat_room:
            post["chat_room_id"] = chat_room["id"]

            # 현재 사용자 참여 여부 확인
            if user_id:
                is_participating = await self.is_user_participant(chat_room["id"], user_id)
                post["is_participating"] = is_participating
            else:
                post["is_participating"] = False
        else:
            post["chat_room_id"] = None
            post["is_participating"] = False

        return post

    async def get_recruiting_posts_paginated(
        self,
        offset: int,
        limit: int = 10,
        campaign_id: Optional[int] = None,
        region: Optional[str] = None,
        is_recruiting: Optional[bool] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """페이지네이션 및 필터링이 적용된 리크루팅 게시글 조회"""
        query = (
            self.supabase
            .table(self.RECRUITING_POST_TABLE)
            .select("*, profiles(user_img, username)")
            .order("created_at", desc=True)
        )

        # 필터링 적용
        if campaign_id:
            query = query.eq("campaign_id", campaign_id)
        if region:
            query = query.eq("region", region)
        if is_recruiting is not None:
            query = query.eq("is_recruiting", is_recruiting)

        # 페이지네이션 적용
        response = query.range(offset, offset + limit - 1).execute()
        posts = response.data if response.data else []

        # 각 게시글에 채팅방 정보 및 참여 여부 추가
        for post in posts:
            chat_room = await self.get_chat_room_by_recruiting_post_id(post["id"])
            if chat_room:
                post["chat_room_id"] = chat_room["id"]

                # 현재 사용자 참여 여부 확인
                if user_id:
                    is_participating = await self.is_user_participant(chat_room["id"], user_id)
                    post["is_participating"] = is_participating
                else:
                    post["is_participating"] = False
            else:
                post["chat_room_id"] = None
                post["is_participating"] = False

        return posts

    async def get_user_participating_posts(
        self,
        user_id: str,
        offset: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """사용자가 참여 중인 리크루팅 게시글 조회"""
        # 1. 사용자가 참여 중인 채팅방 ID 목록 조회
        participant_response = (
            self.supabase
            .table(self.PARTICIPANT_TABLE)
            .select("chat_room_id")
            .eq("user_id", user_id)
            .execute()
        )

        if not participant_response.data:
            return []

        chat_room_ids = [p["chat_room_id"] for p in participant_response.data]

        # 2. 해당 채팅방들의 recruiting_post_id 조회
        room_response = (
            self.supabase
            .table(self.CHAT_ROOM_TABLE)
            .select("recruiting_post_id")
            .in_("id", chat_room_ids)
            .execute()
        )

        if not room_response.data:
            return []

        recruiting_post_ids = [r["recruiting_post_id"] for r in room_response.data]

        # 3. 해당 리크루팅 게시글 조회
        query = (
            self.supabase
            .table(self.RECRUITING_POST_TABLE)
            .select("*, profiles(user_img, username)")
            .in_("id", recruiting_post_ids)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        posts = query.data if query.data else []

        # 채팅방 정보 및 참여 여부 추가
        for post in posts:
            chat_room = await self.get_chat_room_by_recruiting_post_id(post["id"])
            if chat_room:
                post["chat_room_id"] = chat_room["id"]
                post["is_participating"] = True
            else:
                post["chat_room_id"] = None
                post["is_participating"] = False

        return posts

    async def create_recruiting_post(self, post_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """새로운 리크루팅 게시글 생성"""
        # 1단계: INSERT
        insert_response = (
            self.supabase
            .table(self.RECRUITING_POST_TABLE)
            .insert(post_data)
            .execute()
        )

        if not insert_response.data or len(insert_response.data) == 0:
            return None

        # 생성된 게시글의 ID 추출
        created_post_id = insert_response.data[0]["id"]

        # 2단계: 프로필 정보와 함께 조회
        return await self.get_recruiting_post_by_id(created_post_id, str(post_data.get("user_id")))

    async def update_recruiting_post(self, post_id: int, post_data: Dict[str, Any], user_id: str) -> Optional[Dict[str, Any]]:
        """리크루팅 게시글 업데이트"""
        response = (
            self.supabase
            .table(self.RECRUITING_POST_TABLE)
            .update(post_data)
            .eq("id", post_id)
            .execute()
        )

        if response.data and len(response.data) > 0:
            return await self.get_recruiting_post_by_id(post_id, user_id)
        return None

    async def delete_recruiting_post(self, post_id: int) -> bool:
        """리크루팅 게시글 삭제"""
        return await self.delete(self.RECRUITING_POST_TABLE, str(post_id))

    async def increment_current_members(self, post_id: int) -> bool:
        """현재 참여 인원 증가"""
        # 현재 게시글 조회
        post = await self.get_recruiting_post_by_id(post_id)
        if not post:
            return False

        # current_members 증가
        new_count = post["current_members"] + 1
        response = (
            self.supabase
            .table(self.RECRUITING_POST_TABLE)
            .update({"current_members": new_count})
            .eq("id", post_id)
            .execute()
        )
        return response.data is not None

    # ===== ChatRoom 관련 메서드 =====
    async def get_chat_room_by_id(self, room_id: int) -> Optional[Dict[str, Any]]:
        """채팅방 ID로 조회"""
        response = (
            self.supabase
            .table(self.CHAT_ROOM_TABLE)
            .select("*")
            .eq("id", room_id)
            .execute()
        )
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    async def get_chat_room_by_recruiting_post_id(self, recruiting_post_id: int) -> Optional[Dict[str, Any]]:
        """리크루팅 게시글 ID로 채팅방 조회"""
        response = (
            self.supabase
            .table(self.CHAT_ROOM_TABLE)
            .select("*")
            .eq("recruiting_post_id", recruiting_post_id)
            .execute()
        )
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    async def create_chat_room(self, room_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """새로운 채팅방 생성"""
        insert_response = (
            self.supabase
            .table(self.CHAT_ROOM_TABLE)
            .insert(room_data)
            .execute()
        )

        if not insert_response.data or len(insert_response.data) == 0:
            return None

        created_room_id = insert_response.data[0]["id"]
        return await self.get_chat_room_by_id(created_room_id)

    # ===== Participant 관련 메서드 =====
    async def add_participant(self, chat_room_id: int, user_id: str) -> bool:
        """채팅방에 참여자 추가"""
        try:
            insert_response = (
                self.supabase
                .table(self.PARTICIPANT_TABLE)
                .insert({
                    "chat_room_id": chat_room_id,
                    "user_id": user_id
                })
                .execute()
            )
            return insert_response.data is not None
        except Exception:
            # UNIQUE 제약 조건 위반 시 (이미 참여 중)
            return False

    async def is_user_participant(self, chat_room_id: int, user_id: str) -> bool:
        """사용자가 채팅방 참여자인지 확인"""
        response = (
            self.supabase
            .table(self.PARTICIPANT_TABLE)
            .select("id")
            .eq("chat_room_id", chat_room_id)
            .eq("user_id", user_id)
            .execute()
        )
        return response.data is not None and len(response.data) > 0

    async def get_participants_by_room_id(self, chat_room_id: int) -> List[Dict[str, Any]]:
        """채팅방 참여자 목록 조회 (프로필 정보 포함)"""
        response = (
            self.supabase
            .table(self.PARTICIPANT_TABLE)
            .select("*, profiles(user_img, username)")
            .eq("chat_room_id", chat_room_id)
            .order("joined_at", desc=False)
            .execute()
        )
        return response.data if response.data else []

    # ===== ChatMessage 관련 메서드 =====
    async def get_message_by_id(self, message_id: int) -> Optional[Dict[str, Any]]:
        """메시지 ID로 조회 (프로필 정보 포함)"""
        response = (
            self.supabase
            .table(self.CHAT_MESSAGE_TABLE)
            .select("*, profiles(user_img, username)")
            .eq("id", message_id)
            .execute()
        )
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    async def get_messages_by_room_id(
        self,
        chat_room_id: int,
        offset: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """채팅방 ID로 메시지 목록 조회 (프로필 정보 포함, 페이지네이션)"""
        response = (
            self.supabase
            .table(self.CHAT_MESSAGE_TABLE)
            .select("*, profiles(user_img, username)")
            .eq("chat_room_id", chat_room_id)
            .order("created_at", desc=False)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return response.data if response.data else []

    async def create_message(self, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """새로운 메시지 생성"""
        # 1단계: INSERT
        insert_response = (
            self.supabase
            .table(self.CHAT_MESSAGE_TABLE)
            .insert(message_data)
            .execute()
        )

        if not insert_response.data or len(insert_response.data) == 0:
            return None

        # 생성된 메시지의 ID 추출
        created_message_id = insert_response.data[0]["id"]

        # 2단계: 프로필 정보와 함께 조회
        return await self.get_message_by_id(created_message_id)
