"""
분석 결과 모델

LLM 분석 결과를 담는 데이터 구조입니다.
"""

from typing import List

from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    """
    분석 결과 모델

    LLM이 생성한 분석 결과를 담습니다.
    """

    # 중복 제거용 영어 요약
    semantic_summary: str = Field(..., description="중복 제거용 영어 요약 (1,000자 이하)")

    # 사용자용 한국어 요약
    display_summary: str = Field(..., description="사용자용 한국어 요약 (5문장 이내)")

    # 키워드 목록
    keywords: List[str] = Field(..., description="핵심 키워드 목록 (5개 이하)")
