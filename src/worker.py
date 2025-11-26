"""
분석 워커

메시지 처리 루프를 담당합니다.
"""

from src.infrastructure.message_subscriber import MessageSubscriber
from src.logger import get_logger
from src.services.llm_service import LLMService

logger = get_logger("worker")


class Worker:
    """
    분석 워커

    메시지 수신 → LLM 분석 → DB 저장 → 메시지 발행 흐름을 처리합니다.
    """

    def __init__(
        self,
        message_subscriber: MessageSubscriber,
        llm_service: LLMService,
    ):
        self._message_subscriber = message_subscriber
        self._llm_service = llm_service
        self._shutdown = False
        logger.info("Worker 초기화 완료")

    def run(self):
        """
        메인 처리 루프

        종료 요청이 올 때까지 메시지를 처리합니다.
        """
        logger.info("Worker 시작")

        while not self._shutdown:
            # 메시지 수신 (blocking)
            raw_data = self._message_subscriber.receive()

            if raw_data is None:
                # 타임아웃 - 다음 루프로
                continue

            logger.info(
                "메시지 처리 시작",
                message_id=raw_data.message_id,
                source=raw_data.channel,
            )

            # LLM 분석
            analysis_result = self._llm_service.analyze(raw_data.content)

            # TODO: Database.save() 호출
            # TODO: MessagePublisher.publish() 호출

            # 처리 완료 ACK
            self._message_subscriber.ack(raw_data.message_id)
            logger.info("메시지 처리 완료", message_id=raw_data.message_id)

        logger.info("Worker 종료")

    def shutdown(self):
        """종료 요청"""
        logger.info("Worker 종료 요청")
        self._shutdown = True
