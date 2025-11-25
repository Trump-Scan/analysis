"""
분석 워커

메시지 처리 루프를 담당합니다.
"""

import time

from src.logger import get_logger

logger = get_logger("worker")


class Worker:
    """
    분석 워커

    메시지 수신 → LLM 분석 → DB 저장 → 메시지 발행 흐름을 처리합니다.
    """

    def __init__(self):
        self._shutdown = False
        logger.info("Worker 초기화 완료")

    def run(self):
        """
        메인 처리 루프

        종료 요청이 올 때까지 메시지를 처리합니다.
        """
        logger.info("Worker 시작")

        while not self._shutdown:
            logger.debug("loop")
            # TODO: MessageSubscriber.receive() 호출
            # TODO: LLMService.analyze() 호출
            # TODO: Database.save() 호출
            # TODO: MessagePublisher.publish() 호출
            # TODO: MessageSubscriber.ack() 호출

            # 임시: 1초 대기 (실제 구현 시 blocking receive로 대체)
            time.sleep(1)

        logger.info("Worker 종료")

    def shutdown(self):
        """종료 요청"""
        logger.info("Worker 종료 요청")
        self._shutdown = True
