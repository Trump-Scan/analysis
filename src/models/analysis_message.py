"""
분석 결과 메시지 모델

메시지 발행용 데이터 모델입니다. DB 모델(AnalysisData)과 분리하여
원본 데이터의 메타정보를 함께 전달합니다.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AnalysisMessage(BaseModel):
    """
    분석 결과 메시지 모델

    중복 제거 레이어로 발행되는 메시지를 담습니다.
    """

    # DB 필드 (AnalysisData와 동일)
    id: int = Field(..., description="분석 결과 고유 ID")
    raw_data_id: int = Field(..., description="원본 데이터 ID")
    semantic_summary: str = Field(..., description="중복 제거용 영어 요약")
    display_summary: str = Field(..., description="사용자용 한국어 요약")
    keywords: List[str] = Field(..., description="핵심 키워드 목록")
    prompt_version: str = Field(..., description="분석에 사용된 프롬프트 버전")

    # 원본 데이터 정보 (RawData에서 전달)
    channel: Optional[str] = Field(None, description="수집 채널")
    original_link: Optional[str] = Field(None, description="원본 링크")
    published_at: Optional[datetime] = Field(None, description="원본 발행 시각")

    def to_dict(self) -> dict:
        """메시지 발행용 딕셔너리 변환"""
        return {
            "id": self.id,
            "raw_data_id": self.raw_data_id,
            "semantic_summary": self.semantic_summary,
            "display_summary": self.display_summary,
            "keywords": self.keywords,
            "prompt_version": self.prompt_version,
            "channel": self.channel,
            "original_link": self.original_link,
            "published_at": self.published_at.isoformat() if self.published_at else None,
        }
