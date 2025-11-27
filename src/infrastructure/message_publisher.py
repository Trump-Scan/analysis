"""
메시지 발행자

Redis Streams로 메시지를 발행합니다.
"""

import json

import redis

from config import redis as redis_config
from src.logger import get_logger
from src.models.analysis_data import AnalysisData

logger = get_logger("message_publisher")


class MessagePublisher:
    """
    Redis Streams 메시지 발행자

    분석 결과를 다음 레이어로 전달합니다.
    """

    def __init__(self):
        host = redis_config.HOST
        port = redis_config.PORT
        db = redis_config.DB

        self._client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True,
        )
        self._stream = redis_config.OUTPUT_STREAM

        # 연결 테스트
        try:
            self._client.ping()
            logger.info("MessagePublisher 연결 성공", host=host, port=port, db=db)
        except redis.ConnectionError as e:
            logger.error("MessagePublisher 연결 실패", error=str(e))
            raise

    def publish(self, analysis_data: AnalysisData) -> str:
        """
        분석 결과 발행

        Args:
            analysis_data: 발행할 분석 데이터

        Returns:
            발행된 메시지 ID
        """
        try:
            message_json = json.dumps(analysis_data.to_dict(), ensure_ascii=False)
            message_id = self._client.xadd(self._stream, {"data": message_json})

            logger.debug(
                "메시지 발행 완료",
                message_id=message_id,
                analysis_id=analysis_data.id,
            )

            return message_id

        except redis.RedisError as e:
            logger.error("메시지 발행 실패", error=str(e), analysis_id=analysis_data.id)
            raise
        except Exception as e:
            logger.error(
                "메시지 발행 중 예외 발생",
                error=str(e),
                error_type=type(e).__name__,
                analysis_id=analysis_data.id,
            )
            raise

    def close(self):
        """연결 종료"""
        self._client.close()
        logger.info("MessagePublisher 연결 종료")
