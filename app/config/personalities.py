"""성격 타입 정의 - AI 채팅 말투 스타일"""

# 성격 타입 정의
PERSONALITY_TYPES = {
    "friendly": {
        "id": "friendly",
        "name": "친절하고 부드러운",
        "description": "친절하고 부드러운 말투로 대화합니다.",
        "prompt_style": "친절하고 부드러운 말투를 사용하세요. 존댓말을 사용하며, 상냥하고 배려심 있는 톤으로 대화합니다."
    },
    "playful": {
        "id": "playful",
        "name": "텐션 높은 장난꾸러기",
        "description": "텐션이 높고 장난스러운 말투로 대화합니다.",
        "prompt_style": "텐션이 높고 장난스러운 말투를 사용하세요. 재미있는 표현과 이모티콘을 활용하며, 유쾌하고 활기찬 톤으로 대화합니다."
    },
    "researcher": {
        "id": "researcher",
        "name": "연구원 느낌",
        "description": "전문적이고 논리적인 말투로 대화합니다.",
        "prompt_style": "연구원처럼 전문적이고 논리적인 말투를 사용하세요. 데이터와 사실을 중시하며, 분석적이고 객관적인 톤으로 대화합니다."
    },
    "coach": {
        "id": "coach",
        "name": "동기부여하는 코치",
        "description": "열정적으로 동기부여하는 말투로 대화합니다.",
        "prompt_style": "열정적으로 동기부여하는 코치의 말투를 사용하세요. 격려와 응원을 아끼지 않으며, 긍정적이고 에너지 넘치는 톤으로 대화합니다."
    },
    "elegant": {
        "id": "elegant",
        "name": "느긋하면서 품격있는",
        "description": "느긋하고 품격있는 말투로 대화합니다.",
        "prompt_style": "느긋하고 품격있는 말투를 사용하세요. 여유롭고 우아한 표현을 사용하며, 차분하고 세련된 톤으로 대화합니다."
    }
}

# 기본 성격
DEFAULT_PERSONALITY = "friendly"


def get_personality_info(personality_id: str) -> dict:
    """
    성격 ID로 성격 정보 조회

    Args:
        personality_id: 성격 식별자 (friendly, playful, researcher, coach, elegant)

    Returns:
        성격 정보 딕셔너리 (없으면 기본 성격 반환)
    """
    return PERSONALITY_TYPES.get(personality_id, PERSONALITY_TYPES[DEFAULT_PERSONALITY])


def get_available_personalities() -> list:
    """사용 가능한 모든 성격 ID 리스트 반환"""
    return list(PERSONALITY_TYPES.keys())


def get_random_personality() -> dict:
    """
    랜덤 성격 반환 (friendly 제외, 중복 허용)

    friendly는 기본 성격이므로 뽑기에서 제외됩니다.

    Returns:
        랜덤으로 선택된 성격 정보 딕셔너리
    """
    import random
    # friendly를 제외한 성격 목록
    available_personalities = [k for k in PERSONALITY_TYPES.keys() if k != "friendly"]
    personality_id = random.choice(available_personalities)
    return PERSONALITY_TYPES[personality_id]
