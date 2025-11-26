"""
분석 레이어 진입점

트럼프 스캔 서비스의 분석 워커를 실행합니다.
"""

import signal
import sys

from src.infrastructure.message_subscriber import MessageSubscriber
from src.logger import setup_logging, get_logger
from src.services.llm_service import LLMService
from src.worker import Worker

# 로깅 초기화
setup_logging()
logger = get_logger("main")


def main():
    """애플리케이션 진입점"""
    logger.info("분석 레이어 시작")

    # 인프라 컴포넌트 생성
    message_subscriber = MessageSubscriber()

    # 서비스 생성
    llm_service = LLMService()

    # Worker 생성
    worker = Worker(
        message_subscriber=message_subscriber,
        llm_service=llm_service,
    )

    def signal_handler(signum, frame):
        """시그널 핸들러: SIGINT/SIGTERM 처리"""
        sig_name = signal.Signals(signum).name
        logger.info("종료 시그널 수신", signal=sig_name)
        worker.shutdown()

    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Worker 실행
    try:
        worker.run()
    finally:
        message_subscriber.close()

    logger.info("분석 레이어 종료 완료")
    sys.exit(0)


if __name__ == "__main__":
    main()
