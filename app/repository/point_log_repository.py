"""Point Log Repository"""
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, timedelta, date
from app.repository.base_repository import BaseRepository


class PointLogRepository(BaseRepository):
    """포인트 로그 관련 데이터베이스 작업을 처리하는 Repository"""

    TABLE_NAME = "point_log"

    async def create_point_log(
        self,
        user_id: UUID,
        point: int
    ) -> Optional[Dict[str, Any]]:
        """
        포인트 로그 생성

        Parameters:
        -----------
        user_id : UUID
            사용자 ID
        point : int
            포인트 (양수: 획득, 음수: 사용)

        Returns:
        --------
        Optional[Dict[str, Any]]
            생성된 포인트 로그
        """
        log_data = {
            "user_id": str(user_id),
            "point": point,
            "created_at": datetime.now().isoformat()
        }
        return await self.create(self.TABLE_NAME, log_data)

    async def get_logs_by_user(
        self,
        user_id: UUID,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        특정 사용자의 포인트 로그 조회

        Parameters:
        -----------
        user_id : UUID
            사용자 ID
        limit : int
            조회할 최대 개수

        Returns:
        --------
        List[Dict[str, Any]]
            포인트 로그 리스트
        """
        response = (
            self.supabase
            .table(self.TABLE_NAME)
            .select("*")
            .eq("user_id", str(user_id))
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data if response.data else []

    async def get_log_by_id(self, log_id: int) -> Optional[Dict[str, Any]]:
        """포인트 로그 ID로 조회"""
        return await self.find_by_id(self.TABLE_NAME, log_id)

    async def get_total_points_earned(self, user_id: UUID) -> int:
        """
        사용자가 획득한 총 포인트 (양수만)

        Parameters:
        -----------
        user_id : UUID
            사용자 ID

        Returns:
        --------
        int
            총 획득 포인트
        """
        response = (
            self.supabase
            .table(self.TABLE_NAME)
            .select("point")
            .eq("user_id", str(user_id))
            .gt("point", 0)
            .execute()
        )

        if not response.data:
            return 0

        return sum(log["point"] for log in response.data)

    async def get_total_points_spent(self, user_id: UUID) -> int:
        """
        사용자가 사용한 총 포인트 (음수의 절댓값)

        Parameters:
        -----------
        user_id : UUID
            사용자 ID

        Returns:
        --------
        int
            총 사용 포인트 (양수)
        """
        response = (
            self.supabase
            .table(self.TABLE_NAME)
            .select("point")
            .eq("user_id", str(user_id))
            .lt("point", 0)
            .execute()
        )

        if not response.data:
            return 0

        return abs(sum(log["point"] for log in response.data))

    async def get_daily_point_trend(
        self,
        user_id: UUID,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        사용자의 일별 포인트 추이 조회 (최근 N일)

        Parameters:
        -----------
        user_id : UUID
            사용자 ID
        days : int
            조회할 일수 (기본값: 7일)

        Returns:
        --------
        List[Dict[str, Any]]
            일별 포인트 데이터 리스트
            [{"date": "2025-01-20", "total_points": 1250}, ...]
        """
        # 날짜 범위 계산 (최근 N일)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        # 해당 기간의 모든 포인트 로그 조회
        # 날짜 범위를 ISO 형식의 타임스탬프로 변환 (시간 포함)
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date + timedelta(days=1), datetime.min.time())
        
        response = (
            self.supabase
            .table(self.TABLE_NAME)
            .select("point, created_at")
            .eq("user_id", str(user_id))
            .gte("created_at", start_datetime.isoformat())
            .lt("created_at", end_datetime.isoformat())
            .order("created_at", desc=False)
            .execute()
        )

        # 일별로 누적 포인트 계산
        daily_data: Dict[date, int] = {}
        
        # 먼저 해당 기간 이전의 모든 포인트를 합산 (누적 포인트 계산을 위해)
        before_period_response = (
            self.supabase
            .table(self.TABLE_NAME)
            .select("point")
            .eq("user_id", str(user_id))
            .lt("created_at", start_datetime.isoformat())
            .execute()
        )
        
        cumulative_points = 0
        if before_period_response.data:
            cumulative_points = sum(log["point"] for log in before_period_response.data)

        # 조회 기간 내의 포인트 로그 처리
        if response.data:
            for log in response.data:
                log_date = datetime.fromisoformat(log["created_at"].replace("Z", "+00:00")).date()
                cumulative_points += log["point"]
                # 해당 날짜의 마지막 누적 포인트 저장
                daily_data[log_date] = cumulative_points

        # 실제 사용자의 총 포인트 조회 (profiles 테이블에서)
        user_response = (
            self.supabase
            .table("profiles")
            .select("total_points")
            .eq("id", str(user_id))
            .single()
            .execute()
        )
        
        actual_total_points = user_response.data.get("total_points", 0) if user_response.data else 0

        # 결과 변환 (날짜별로 정렬된 리스트)
        result = []
        # 조회 기간 이전의 누적 포인트로 시작 (데이터가 없으면 이 값 사용)
        current_points = cumulative_points if not daily_data else 0

        for day_offset in range(days):
            current_date = start_date + timedelta(days=day_offset)

            # 해당 날짜에 데이터가 있으면 업데이트
            if current_date in daily_data:
                current_points = daily_data[current_date]

            # 마지막 날짜(오늘)는 실제 사용자의 총 포인트로 설정
            if current_date == end_date:
                current_points = actual_total_points

            # 모든 날짜에 대해 결과 추가 (데이터가 없어도 이전 누적 포인트 표시)
            result.append({
                "date": current_date.isoformat(),
                "total_points": current_points
            })

        return result
