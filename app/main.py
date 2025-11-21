from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import router
# from app.core.logging_config import setup_logging
# import os

# # 로깅 설정
# log_level = os.getenv("LOG_LEVEL", "INFO")
# log_file = os.getenv("LOG_FILE", "logs/zeroro.log")
# setup_logging(log_level=log_level, log_file=log_file)

app = FastAPI(
    title="ZeroRo Backend API",
    description="환경 보호 앱 ZeroRo의 백엔드 API 서버",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 허용 도메인
# TODO: EC2 생성 시 IP 추가 - JOJO
origins = [
  "http://localhost",
  "https://localhost:8000",
  "http://127.0.0.1:8000",
  "http://10.0.2.2:8000"  # Android 에뮬레이터용
] 

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,  # 인증 정보(cookie, verify header 등) 허용 여부
  allow_methods=["*"],     # 모든 HTTP method 허용
  allow_headers=["*"]      # 모든 HTTP 헤더 허용
)

@app.get("/")
async def root():
    return {
        "message": "ZeroRo Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# API 라우터 확장
app.include_router(router, prefix="/api/v1")