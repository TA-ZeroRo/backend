"""
간단한 RPA 구조 테스트 (Playwright 없이 실행 가능)

실행 방법:
pytest tests/test_rpa_simple.py -v -s
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_repository_imports():
    """Repository import 테스트"""
    from app.repository.rpa_config_repository import RPAConfigRepository
    from app.repository.mission_template_repository import MissionTemplateRepository

    rpa_repo = RPAConfigRepository()
    mission_repo = MissionTemplateRepository()

    assert rpa_repo is not None
    assert mission_repo is not None
    print("✅ Repository imports OK")


def test_service_imports():
    """Service import 테스트 (Playwright 없이)"""
    # RPA Config Service는 Playwright 의존성 없음
    from app.services.rpa_config_service import RPAConfigService

    service = RPAConfigService()
    assert service is not None
    print("✅ RPA Config Service import OK")


def test_schemas():
    """Pydantic 스키마 테스트"""
    from app.schemas.rpa_config_schemas import (
        RPAConfigCreate,
        RPAConfigResponse,
        SelectorStrategy
    )
    from app.schemas.mission_template_schemas import MissionTemplateBase

    # RPA Config 스키마 테스트
    config_data = {
        "site_code": "test_site",
        "site_name": "테스트 사이트",
        "base_url": "https://example.com",
        "login_url": "https://example.com/login",
        "login_config": {
            "selectors": {
                "username_input": "#username",
                "password_input": "#password",
                "submit_button": "button"
            }
        },
        "form_config": {
            "selectors": {
                "submit_button": "#submit"
            }
        }
    }

    config = RPAConfigCreate(**config_data)
    assert config.site_code == "test_site"
    print("✅ RPA Config schema OK")

    # Mission Template 스키마 테스트 (rpa_site_config_id 필드 있는지)
    from app.schemas.mission_template_schemas import MissionTemplateCreate

    # rpa_site_config_id 필드가 있어야 함
    mission_data = {
        "campaign_id": 1,
        "title": "테스트 미션",
        "verification_type": "RPA_ACTION",
        "rpa_site_config_id": 1
    }

    mission = MissionTemplateCreate(**mission_data)
    assert mission.rpa_site_config_id == 1
    print("✅ Mission Template schema has rpa_site_config_id field")


def test_config_validation():
    """설정 검증 로직 테스트"""
    import asyncio
    from app.services.rpa_config_service import RPAConfigService

    async def run_test():
        service = RPAConfigService()

        # 유효한 설정
        valid_config = {
            "site_code": "test",
            "site_name": "Test Site",
            "base_url": "https://example.com",
            "login_url": "https://example.com/login",
            "login_config": {
                "selectors": {
                    "username_input": "#username",
                    "password_input": "#password",
                    "submit_button": "button[type='submit']"
                }
            },
            "form_config": {
                "selectors": {
                    "submit_button": "#submit"
                }
            }
        }

        is_valid, error = await service.validate_config(valid_config)
        assert is_valid is True
        assert error is None
        print("✅ Valid config passed validation")

        # 무효한 설정 (필수 필드 누락)
        invalid_config = {
            "site_code": "test"
            # Missing required fields
        }

        is_valid, error = await service.validate_config(invalid_config)
        assert is_valid is False
        assert error is not None
        print(f"✅ Invalid config failed validation: {error}")

        # 로그인 셀렉터 누락
        missing_login_selector = {
            "site_code": "test",
            "site_name": "Test",
            "base_url": "https://example.com",
            "login_url": "https://example.com/login",
            "login_config": {
                "selectors": {
                    "username_input": "#username"
                    # Missing password_input and submit_button
                }
            },
            "form_config": {
                "selectors": {
                    "submit_button": "#submit"
                }
            }
        }

        is_valid, error = await service.validate_config(missing_login_selector)
        assert is_valid is False
        assert "login selector" in error.lower()
        print(f"✅ Missing login selector detected: {error}")

    asyncio.run(run_test())


def test_field_mapping_logic():
    """필드 매핑 로직 테스트"""
    # Mock 시나리오: submission_data -> selector 변환

    field_mapping = {
        "user_name": "name_input",
        "user_phone": "phone_input"
    }

    form_config = {
        "selectors": {
            "name_input": "input[name='name']",
            "phone_input": "#phone"
        }
    }

    submission_data = {
        "user_name": "홍길동",
        "user_phone": "01012345678"
    }

    # 변환 테스트
    for data_key, data_value in submission_data.items():
        selector_key = field_mapping.get(data_key)
        assert selector_key is not None, f"No mapping for {data_key}"

        selector = form_config['selectors'].get(selector_key)
        assert selector is not None, f"No selector for {selector_key}"

        print(f"✅ {data_key} ({data_value}) → {selector_key} → {selector}")


def test_self_healing_strategy_structure():
    """Self-Healing 전략 구조 테스트"""
    strategies = {
        "username_input": [
            {"selector": "#username", "priority": 1, "method": "id"},
            {"selector": "input[name='username']", "priority": 2, "method": "name"},
            {"selector": ".login-input", "priority": 3, "method": "class"}
        ]
    }

    # 우선순위 정렬 테스트
    username_strategies = strategies["username_input"]
    sorted_strategies = sorted(username_strategies, key=lambda x: x.get('priority', 999))

    assert sorted_strategies[0]['priority'] == 1
    assert sorted_strategies[0]['selector'] == "#username"
    assert sorted_strategies[1]['priority'] == 2
    assert sorted_strategies[2]['priority'] == 3

    print("✅ Self-Healing strategy sorting works correctly")


def test_migration_sql_syntax():
    """마이그레이션 SQL 파일 존재 확인"""
    migration_file = Path(__file__).parent.parent / "database" / "migrations" / "004_create_rpa_site_configs.sql"
    seed_file = Path(__file__).parent.parent / "database" / "seeds" / "001_seed_rpa_configs.sql"

    assert migration_file.exists(), f"Migration file not found: {migration_file}"
    assert seed_file.exists(), f"Seed file not found: {seed_file}"

    # 파일 내용 확인
    migration_content = migration_file.read_text(encoding='utf-8')
    assert "CREATE TABLE IF NOT EXISTS rpa_site_configs" in migration_content
    assert "ALTER TABLE mission_templates" in migration_content
    assert "rpa_site_config_id" in migration_content

    seed_content = seed_file.read_text(encoding='utf-8')
    assert "seoul_ecomileage_mock" in seed_content
    assert "selector_strategies" in seed_content
    assert "field_mapping" in seed_content

    print("✅ Migration and seed files exist and contain correct content")


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "-s"])
