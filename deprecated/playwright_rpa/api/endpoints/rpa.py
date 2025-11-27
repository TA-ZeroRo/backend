"""RPA Execution Endpoint"""
from fastapi import APIRouter, HTTPException, status
from app.schemas.rpa_execute_schemas import RPAExecuteRequest, RPAExecuteResponse
from app.services.rpa_execution_service import RPAExecutionService
import logging

router = APIRouter()
rpa_service = RPAExecutionService()
logger = logging.getLogger(__name__)


@router.post(
    "/execute",
    response_model=RPAExecuteResponse,
    status_code=status.HTTP_200_OK,
    summary="RPA 실행",
    description="""
    Campaign ID와 제출 데이터를 받아 RPA를 실행합니다.

    - Campaign에 설정된 폼 설정 (rpa_form_config, rpa_field_mapping)
    - RPA Site Config에 설정된 로그인 설정 (login_config)
    - 제공된 credentials로 자동 로그인 및 폼 제출

    **주의**: RPA 실행은 실제 브라우저를 실행하므로 시간이 오래 걸릴 수 있습니다 (10-30초).
    """
)
async def execute_rpa(request: RPAExecuteRequest) -> RPAExecuteResponse:
    """
    RPA 실행 엔드포인트

    Parameters:
    -----------
    request : RPAExecuteRequest
        - campaign_id: 실행할 Campaign ID
        - submission_data: 폼에 제출할 데이터 (field_mapping 키 사용)
        - credentials: 로그인 인증 정보 {"username": "...", "password": "..."}

    Returns:
    --------
    RPAExecuteResponse
        - success: 실행 성공 여부
        - message: 성공 메시지
        - error: 에러 메시지 (실패 시)
        - execution_time: 실행 시간 (초)
        - campaign_id: 실행된 Campaign ID

    Raises:
    -------
    HTTPException (500)
        RPA 실행 중 예상치 못한 에러 발생 시
    """
    try:
        logger.info(f"RPA execution request received for campaign_id={request.campaign_id}")

        result = await rpa_service.execute_rpa_for_campaign(
            campaign_id=request.campaign_id,
            submission_data=request.submission_data,
            credentials=request.credentials
        )

        logger.info(
            f"RPA execution completed: campaign_id={request.campaign_id}, "
            f"success={result.get('success')}"
        )

        return RPAExecuteResponse(**result)

    except Exception as e:
        logger.exception(f"Unexpected error in RPA execution endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RPA execution failed: {str(e)}"
        )


@router.get(
    "/health",
    summary="RPA 헬스체크",
    description="RPA 서비스가 정상 동작하는지 확인합니다."
)
async def health_check():
    """RPA 서비스 헬스체크"""
    return {
        "status": "healthy",
        "service": "RPA Execution Service",
        "message": "RPA service is running"
    }
