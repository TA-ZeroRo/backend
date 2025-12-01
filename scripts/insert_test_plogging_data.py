"""테스트 플로깅 데이터 삽입 스크립트"""
import os
import sys
from datetime import datetime, timedelta
from uuid import uuid4

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client

# Supabase 설정
SUPABASE_URL = "https://aldghxocvhbscghaztfk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFsZGdoeG9jdmhic2NnaGF6dGZrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA5MzkyNjIsImV4cCI6MjA2NjUxNTI2Mn0.3iBz_bIoB7cS2MyTch3Jm6FlXAdLj0DrBXG7UipTO_w"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def generate_route_points(start_lat, start_lng, num_points=20, spread=0.005):
    """GPS 경로 포인트 생성"""
    import random

    points = []
    current_lat = start_lat
    current_lng = start_lng
    base_time = datetime.utcnow() - timedelta(hours=1)

    for i in range(num_points):
        points.append({
            "lat": current_lat,
            "lng": current_lng,
            "timestamp": (base_time + timedelta(minutes=i * 2)).isoformat(),
            "accuracy": random.uniform(5.0, 15.0)
        })
        # 약간씩 이동
        current_lat += random.uniform(-spread/10, spread/10)
        current_lng += random.uniform(-spread/10, spread/10)

    return points


def calculate_bounds(points):
    """경로의 bounding box 계산"""
    lats = [p["lat"] for p in points]
    lngs = [p["lng"] for p in points]
    return {
        "min_lat": min(lats),
        "max_lat": max(lats),
        "min_lng": min(lngs),
        "max_lng": max(lngs)
    }


def calculate_distance(points):
    """총 거리 계산 (미터)"""
    from math import radians, cos, sin, sqrt, atan2

    total = 0
    for i in range(1, len(points)):
        lat1, lng1 = radians(points[i-1]["lat"]), radians(points[i-1]["lng"])
        lat2, lng2 = radians(points[i]["lat"]), radians(points[i]["lng"])

        dlat = lat2 - lat1
        dlng = lng2 - lng1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        total += 6371000 * c  # 지구 반지름 (미터)

    return total


# 테스트 경로 데이터 (서울 주요 지역)
TEST_ROUTES = [
    {
        "name": "광화문 광장",
        "start_lat": 37.5759,
        "start_lng": 126.9769,
        "intensity": 2
    },
    {
        "name": "청계천",
        "start_lat": 37.5696,
        "start_lng": 126.9784,
        "intensity": 1
    },
    {
        "name": "여의도 한강공원",
        "start_lat": 37.5284,
        "start_lng": 126.9340,
        "intensity": 3
    },
    {
        "name": "반포 한강공원",
        "start_lat": 37.5108,
        "start_lng": 126.9955,
        "intensity": 2
    },
    {
        "name": "뚝섬 한강공원",
        "start_lat": 37.5300,
        "start_lng": 127.0650,
        "intensity": 1
    },
]


def insert_test_data():
    """테스트 데이터 삽입"""
    test_user_id = str(uuid4())
    print(f"테스트 사용자 ID: {test_user_id}")

    for route_info in TEST_ROUTES:
        print(f"\n{route_info['name']} 플로깅 데이터 삽입 중...")

        # 경로 포인트 생성
        route_points = generate_route_points(
            route_info["start_lat"],
            route_info["start_lng"],
            num_points=25
        )
        bounds = calculate_bounds(route_points)
        distance = calculate_distance(route_points)
        duration = len(route_points) * 2  # 포인트당 2분

        started_at = datetime.utcnow() - timedelta(days=1, hours=route_info["intensity"])
        ended_at = started_at + timedelta(minutes=duration)

        # 1. 세션 생성
        session_data = {
            "user_id": test_user_id,
            "status": "COMPLETED",
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
            "duration_minutes": duration,
            "total_distance_meters": distance,
            "intensity_level": route_info["intensity"],
            "verification_count": 2,
            "points_earned": 100 + (route_info["intensity"] * 50)
        }

        session_result = supabase.table("plogging_sessions").insert(session_data).execute()

        if session_result.data:
            session_id = session_result.data[0]["id"]
            print(f"  세션 생성됨: ID={session_id}")

            # 2. 경로 저장
            route_data = {
                "session_id": session_id,
                "route_points": route_points,
                "point_count": len(route_points),
                "min_lat": bounds["min_lat"],
                "max_lat": bounds["max_lat"],
                "min_lng": bounds["min_lng"],
                "max_lng": bounds["max_lng"]
            }

            route_result = supabase.table("plogging_routes").insert(route_data).execute()

            if route_result.data:
                print(f"  경로 저장됨: {len(route_points)}개 포인트, 거리={distance:.0f}m")
            else:
                print(f"  경로 저장 실패")
        else:
            print(f"  세션 생성 실패")

    print("\n" + "="*50)
    print("테스트 데이터 삽입 완료!")
    print(f"테스트 사용자 ID: {test_user_id}")
    print("="*50)


if __name__ == "__main__":
    insert_test_data()
