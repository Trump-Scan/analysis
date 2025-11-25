"""
입력 데이터 모델

데이터 수집 레이어에서 전달받는 원본 데이터 구조입니다.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class RawData(BaseModel):
    """
    원본 데이터 모델

    데이터 수집 레이어에서 Redis Streams를 통해 전달받는 데이터입니다.
    """

    # 메시지 식별자 (Redis Stream message ID)
    message_id: str = Field(..., description="Redis Stream 메시지 ID")

    # 원본 데이터 필드
    id: int = Field(..., description="ID")
    content: str = Field(..., description="포스트 내용")
    link: str = Field(..., description="포스트 링크")
    published_at: datetime = Field(..., description="발행 시간")
    channel: str = Field(..., description="수집 채널")
