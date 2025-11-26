# Playwright RPA (Deprecated)

## ⚠️ Deprecation Notice

이 코드는 **2025년 1월 22일**에 deprecated 되었습니다.

### Deprecated 이유

1. **서버 리소스 과다 사용**: Playwright 기반 백엔드 브라우저 자동화는 서버 메모리와 CPU를 많이 소비
2. **모바일 환경 비효율**: 모바일 앱에서 백엔드 RPA는 사용자 경험이 좋지 않음
3. **보안 이슈**: 사용자 로그인 정보를 서버로 전송해야 하는 보안 문제
4. **유지보수 어려움**: 웹사이트 변경 시 셀렉터 전략 업데이트 필요

### 대체 솔루션

새로운 **JavaScript Channel WebView RPA** 시스템으로 전환:

- **위치**: `backend/app/api/v1/endpoints/rpa_webview.py`
- **문서**: `backend/docs/WEBVIEW_RPA_GUIDE.md`
- **핵심 개선사항**:
  - 사용자가 Flutter WebView에서 직접 로그인
  - 백엔드는 JavaScript 코드 생성만 담당
  - JavaScript Channel로 양방향 통신
  - 서버 리소스 절약

### 보관 이유

1. **참고 자료**: Self-Healing Adapter 패턴 재사용 가능
2. **롤백 가능성**: 긴급 상황 시 복구 옵션
3. **히스토리 보존**: 기술적 의사결정 기록

### 기존 구조

```
deprecated/playwright_rpa/
├── api/endpoints/
│   └── rpa.py                    # RPA 실행 API 엔드포인트
├── services/
│   ├── rpa_core.py               # Playwright 자동화 코어
│   ├── rpa_execution_service.py  # RPA 실행 오케스트레이션
│   ├── rpa_config_service.py     # RPA 설정 관리
│   └── rpa_adapters/
│       ├── base.py               # Self-Healing Adapter
│       └── default_strategies.py # 기본 셀렉터 전략
├── repository/
│   └── rpa_config_repository.py  # RPA 설정 DB 액세스
├── schemas/
│   ├── rpa_config_schemas.py     # RPA 설정 Pydantic 모델
│   └── rpa_execute_schemas.py    # RPA 실행 Pydantic 모델
├── database/
│   ├── migrations/
│   │   ├── 004_create_rpa_site_configs.sql
│   │   ├── 004_rollback_rpa_site_configs.sql
│   │   └── 005_create_hybrid_rpa_structure.sql
│   └── seeds/
│       └── 001_seed_rpa_configs.sql
├── tests/
│   ├── test_rpa_simple.py
│   ├── test_rpa_core.py
│   ├── test_rpa_integration.py
│   ├── test_zeroseoul_rpa.py
│   ├── test_kgreener_rpa_debug.py
│   ├── test_rpa_debug.py
│   └── manual/
│       └── test_rpa_manual.py
├── docs/
│   ├── RPA_SETUP_GUIDE.md
│   ├── HYBRID_RPA_STRUCTURE.md
│   ├── RPA_IMPLEMENTATION_STATUS.md
│   ├── RPA_MCP_WORKFLOW.md
│   ├── RPA_MCP_RULES.md
│   └── RPA_MCP_QUICK_REFERENCE.md
└── requirements-rpa.txt          # Playwright 의존성
```

### 주요 기능

- **Self-Healing Adapter**: 우선순위 기반 셀렉터 전략으로 웹사이트 변경에 대응
- **Hybrid RPA 구조**: 로그인 설정 공유 + 캠페인별 폼 설정
- **자동 재시도**: 셀렉터 실패 시 다음 전략 자동 시도
- **스크린샷 캡처**: 에러 발생 시 디버깅용 스크린샷 저장

### 기술 스택

- Playwright (v1.40.0)
- FastAPI
- PostgreSQL (rpa_site_configs 테이블)
- Pydantic (스키마 검증)

### 참고 링크

- [새로운 WebView RPA 가이드](../docs/WEBVIEW_RPA_GUIDE.md)
- [WebView RPA API 문서](../docs/WEBVIEW_RPA_API.md)
- [Deprecation 결정 문서](../docs/DEPRECATION_DECISION.md)

---

**Last Updated**: 2025-01-22
**Deprecated By**: Claude Code
**Contact**: 문의 사항은 프로젝트 관리자에게 연락하세요
