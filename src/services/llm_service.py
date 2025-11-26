"""
LLM 서비스

Gemini API를 호출하여 분석을 수행합니다.
"""

import json

from google import genai
from google.genai import types

from config import llm as llm_config
from src.logger import get_logger
from src.models.analysis_result import AnalysisResult
from src.services.prompts import ANALYSIS_SYSTEM_PROMPT

logger = get_logger("llm_service")


class LLMService:
    """
    LLM 분석 서비스

    Gemini API를 호출하여 콘텐츠를 분석합니다.
    """

    def __init__(self):
        self._model_name = llm_config.MODEL_NAME
        self._client = genai.Client(api_key=llm_config.API_KEY)

        # API 키 유효성 확인
        self._verify_connection()

        logger.info("LLMService 초기화 완료", model=self._model_name)

    def _verify_connection(self):
        """API 키 유효성 확인"""
        try:
            list(self._client.models.list())
            logger.debug("Gemini API 연결 확인 완료")
        except Exception as e:
            logger.error("Gemini API 연결 실패", error=str(e))
            raise

    def analyze(self, content: str) -> AnalysisResult:
        """
        콘텐츠 분석

        Args:
            content: 분석할 본문 내용

        Returns:
            분석 결과
        """
        logger.debug("LLM 분석 시작")

        # API 호출
        response = self._client.models.generate_content(
            model=self._model_name,
            contents=content,
            config=types.GenerateContentConfig(
                system_instruction=ANALYSIS_SYSTEM_PROMPT,
                response_mime_type="application/json",
            ),
        )

        # JSON 파싱
        result_dict = json.loads(response.text)

        # AnalysisResult 생성
        analysis_result = AnalysisResult(
            semantic_summary=result_dict["semantic_summary"],
            display_summary=result_dict["display_summary"],
            keywords=result_dict["keywords"],
        )

        logger.debug("LLM 분석 완료",
                     semantic_summary=analysis_result.semantic_summary,
                     display_summary=analysis_result.display_summary,
                     keywords=analysis_result.keywords)

        return analysis_result
