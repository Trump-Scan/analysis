"""
분석 레이어 진입점

트럼프 스캔 서비스의 분석 워커를 실행합니다.
"""

import signal
import sys

from src.logger import setup_logging, get_logger
from src.worker import Worker

# 로깅 초기화
setup_logging()
logger = get_logger("main")


def main():
    """애플리케이션 진입점"""
    logger.info("분석 레이어 시작")

    # Worker 생성
    worker = Worker()

    def signal_handler(signum, frame):
        """시그널 핸들러: SIGINT/SIGTERM 처리"""
        sig_name = signal.Signals(signum).name
        logger.info("종료 시그널 수신", signal=sig_name)
        worker.shutdown()

    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Worker 실행
    worker.run()

    logger.info("분석 레이어 종료 완료")
    sys.exit(0)


if __name__ == "__main__":
    main()
