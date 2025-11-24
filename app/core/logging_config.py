"""Logging Configuration for ZeroRo Backend"""
import logging
import sys
from typing import Optional
from pathlib import Path


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> None:
    """
    애플리케이션 전역 로깅 설정

    Parameters:
    -----------
    log_level : str
        로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    log_file : Optional[str]
        로그 파일 경로 (None이면 콘솔만 출력)
    log_format : Optional[str]
        커스텀 로그 포맷 (None이면 기본 포맷 사용)
    """
    # 로그 레벨 설정
    level = getattr(logging, log_level.upper(), logging.INFO)

    # 기본 로그 포맷
    if log_format is None:
        log_format = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "[%(filename)s:%(lineno)d] - %(message)s"
        )

    # 날짜 포맷
    date_format = "%Y-%m-%d %H:%M:%S"

    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 포매터 생성
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # 콘솔 핸들러 추가
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 파일 핸들러 추가 (선택적)
    if log_file:
        # 로그 디렉토리 생성
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # 특정 로거의 로그 레벨 조정
    # Playwright 로그는 WARNING 이상만 표시
    logging.getLogger('playwright').setLevel(logging.WARNING)

    # HTTP 관련 로그는 WARNING 이상만 표시
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)

    # Supabase 로그 레벨 조정
    logging.getLogger('supabase').setLevel(logging.WARNING)
    logging.getLogger('postgrest').setLevel(logging.WARNING)

    logging.info(f"Logging configured with level: {log_level}")
    if log_file:
        logging.info(f"Logs will be written to: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    이름으로 로거 인스턴스 가져오기

    Parameters:
    -----------
    name : str
        로거 이름 (일반적으로 __name__ 사용)

    Returns:
    --------
    logging.Logger
        로거 인스턴스
    """
    return logging.getLogger(name)


# RPA 전용 로거 설정
def setup_rpa_logger(log_file: str = "logs/rpa.log") -> logging.Logger:
    """
    RPA 작업 전용 로거 설정

    Parameters:
    -----------
    log_file : str
        RPA 로그 파일 경로

    Returns:
    --------
    logging.Logger
        RPA 전용 로거
    """
    rpa_logger = logging.getLogger('rpa')
    rpa_logger.setLevel(logging.DEBUG)

    # 파일 핸들러
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - RPA - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)

    rpa_logger.addHandler(file_handler)

    return rpa_logger
