"""
분석 데이터 모델

DB에 저장되는 분석 결과 레코드입니다.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class AnalysisData(BaseModel):
    """
    분석 데이터 모델

    DB에 저장되는 분석 결과 레코드를 담습니다.
    """

    # DB 필드
    id: Optional[int] = Field(None, description="분석 결과 고유 ID (자동 생성)")
    raw_data_id: int = Field(..., description="원본 데이터 ID")

    # LLM 분석 결과
    semantic_summary: str = Field(..., description="중복 제거용 영어 요약")
    display_summary: str = Field(..., description="사용자용 한국어 요약")
    keywords: List[str] = Field(..., description="핵심 키워드 목록")
    prompt_version: str = Field(..., description="분석에 사용된 프롬프트 버전")

    def to_dict(self) -> dict:
        """메시지 발행용 딕셔너리 변환"""
        return {
            "id": self.id,
            "raw_data_id": self.raw_data_id,
            "semantic_summary": self.semantic_summary,
            "display_summary": self.display_summary,
            "keywords": self.keywords,
            "prompt_version": self.prompt_version,
        }
