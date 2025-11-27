"""
LLMService 테스트
"""

from src.logger import setup_logging, get_logger
from src.services.llm_service import LLMService

# 로깅 설정
setup_logging()
logger = get_logger("test")


def test_llm_service():
    """LLMService 분석 테스트"""

    # 테스트 데이터
    content = "Whatever happened to \"Senator\" Rand Paul? He was never great, but he went really BAD! I got him elected, TWICE (in the Great Commonwealth of Kentucky!), but he just never votes positively for the Republican Party. He's a nasty liddle' guy, much like \"Congressman\" Thomas Massie, aka Rand Paul Jr., also of Kentucky (which I won three times, in massive landslides!), a sick Wacko, who refuses to vote for our great Republican Party, MAGA, or America First. It's really weird!!!"

    logger.info("테스트 시작")
    logger.info("원본 내용", content=content[:100] + "...")

    # LLMService 생성 및 분석
    llm_service = LLMService()
    result = llm_service.analyze(content)

    # 결과 출력
    logger.info("=== 분석 결과 ===")
    logger.info("Semantic Summary", summary=result.semantic_summary)
    logger.info("Display Summary", summary=result.display_summary)
    logger.info("Keywords", keywords=result.keywords)
    logger.info("Prompt Version", prompt_version=result.prompt_version)

    # 검증
    assert result.semantic_summary, "semantic_summary가 비어있음"
    assert result.display_summary, "display_summary가 비어있음"
    assert len(result.keywords) > 0, "keywords가 비어있음"
    assert len(result.keywords) <= 5, "keywords가 5개 초과"

    logger.info("테스트 통과!")


if __name__ == "__main__":
    test_llm_service()
