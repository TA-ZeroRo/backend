"""Firebase Admin SDK 초기화 설정"""
import os
import firebase_admin
from firebase_admin import credentials, messaging
from dotenv import load_dotenv

load_dotenv()

# Firebase 서비스 계정 키 경로
FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "./firebase-service-account.json")

_firebase_app = None


def initialize_firebase():
    """Firebase Admin SDK 초기화"""
    global _firebase_app

    if _firebase_app is not None:
        return _firebase_app

    # 서비스 계정 키 파일 존재 여부 확인
    if not os.path.exists(FIREBASE_SERVICE_ACCOUNT_PATH):
        print(f"Warning: Firebase service account file not found at {FIREBASE_SERVICE_ACCOUNT_PATH}")
        print("Push notifications will not work until the file is configured.")
        return None

    try:
        cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_PATH)
        _firebase_app = firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized successfully")
        return _firebase_app
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {e}")
        return None


def get_firebase_app():
    """Firebase 앱 인스턴스 반환"""
    global _firebase_app
    if _firebase_app is None:
        _firebase_app = initialize_firebase()
    return _firebase_app


def is_firebase_initialized() -> bool:
    """Firebase가 초기화되었는지 확인"""
    return _firebase_app is not None
