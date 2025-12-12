"""FCM Service - 푸시 알림 발송 로직"""
from typing import List, Dict, Any, Optional
from firebase_admin import messaging
from app.core.firebase_config import is_firebase_initialized, get_firebase_app
from app.repository.fcm_token_repository import FcmTokenRepository
from app.schemas.fcm_schemas import ChatPushNotification


class FcmService:
    """FCM 푸시 알림 발송 서비스"""

    def __init__(self):
        self.fcm_token_repo = FcmTokenRepository()

    async def register_token(self, user_id: str, fcm_token: str, platform: str) -> Optional[Dict[str, Any]]:
        """FCM 토큰 등록"""
        return await self.fcm_token_repo.register_token(user_id, fcm_token, platform)

    async def delete_token(self, user_id: str, fcm_token: str) -> bool:
        """FCM 토큰 삭제"""
        return await self.fcm_token_repo.delete_token(user_id, fcm_token)

    async def send_chat_notification(
        self,
        notification_data: ChatPushNotification,
        recipient_user_ids: List[str]
    ) -> Dict[str, Any]:
        """채팅 메시지 푸시 알림 발송"""
        result = {
            "success_count": 0,
            "failure_count": 0,
            "invalid_tokens": []
        }

        # Firebase 초기화 확인
        if not is_firebase_initialized():
            print("Firebase not initialized. Skipping push notification.")
            return result

        # 수신자들의 FCM 토큰 조회
        tokens_data = await self.fcm_token_repo.get_tokens_by_user_ids(recipient_user_ids)

        if not tokens_data:
            return result

        # 메시지 본문 생성 (미리보기용으로 20자 제한)
        message_preview = notification_data.message
        if len(message_preview) > 20:
            message_preview = message_preview[:20] + "..."

        # 알림 제목 생성
        title = notification_data.sender_name
        if notification_data.recruiting_title:
            title = f"{notification_data.recruiting_title}"

        # 각 토큰에 대해 푸시 발송
        for token_data in tokens_data:
            fcm_token = token_data["fcm_token"]

            try:
                # FCM 메시지 생성
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=f"{notification_data.sender_name}: {message_preview}"
                    ),
                    data={
                        "type": "chat_message",
                        "chat_room_id": str(notification_data.chat_room_id),
                        "sender_id": notification_data.sender_id,
                        "sender_name": notification_data.sender_name,
                        "recruiting_post_id": str(notification_data.recruiting_post_id) if notification_data.recruiting_post_id else "",
                        "click_action": "FLUTTER_NOTIFICATION_CLICK"
                    },
                    token=fcm_token,
                    # Android 설정
                    android=messaging.AndroidConfig(
                        priority="high",
                        notification=messaging.AndroidNotification(
                            channel_id="chat_messages",
                            priority="high",
                            default_sound=True
                        )
                    ),
                    # iOS 설정
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                alert=messaging.ApsAlert(
                                    title=title,
                                    body=f"{notification_data.sender_name}: {message_preview}"
                                ),
                                sound="default",
                                badge=1
                            )
                        )
                    )
                )

                # 메시지 발송
                messaging.send(message)
                result["success_count"] += 1

            except messaging.UnregisteredError:
                # 토큰이 유효하지 않음 - 삭제
                result["invalid_tokens"].append(fcm_token)
                result["failure_count"] += 1
                await self.fcm_token_repo.delete_invalid_token(fcm_token)

            except Exception as e:
                print(f"Error sending FCM message: {e}")
                result["failure_count"] += 1

        return result

    async def send_multicast_notification(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """여러 토큰에 동시에 알림 발송 (배치 발송)"""
        result = {
            "success_count": 0,
            "failure_count": 0,
            "invalid_tokens": []
        }

        if not is_firebase_initialized():
            print("Firebase not initialized. Skipping push notification.")
            return result

        if not tokens:
            return result

        try:
            # MulticastMessage 생성
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=tokens,
                android=messaging.AndroidConfig(
                    priority="high",
                    notification=messaging.AndroidNotification(
                        channel_id="chat_messages",
                        priority="high",
                        default_sound=True
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound="default",
                            badge=1
                        )
                    )
                )
            )

            # 배치 발송
            response = messaging.send_each_for_multicast(message)

            result["success_count"] = response.success_count
            result["failure_count"] = response.failure_count

            # 실패한 토큰 처리
            for idx, send_response in enumerate(response.responses):
                if not send_response.success:
                    if isinstance(send_response.exception, messaging.UnregisteredError):
                        result["invalid_tokens"].append(tokens[idx])
                        await self.fcm_token_repo.delete_invalid_token(tokens[idx])

        except Exception as e:
            print(f"Error sending multicast FCM message: {e}")
            result["failure_count"] = len(tokens)

        return result
