"""
분석 레이어 진입점

트럼프 스캔 서비스의 분석 워커를 실행합니다.
"""

import signal
import sys


def main():
    """애플리케이션 진입점"""
    print("분석 레이어 시작...")

    # 종료 이벤트 처리를 위한 플래그
    shutdown_requested = False

    def signal_handler(signum, frame):
        """시그널 핸들러: SIGINT/SIGTERM 처리"""
        nonlocal shutdown_requested
        sig_name = signal.Signals(signum).name
        print(f"\n{sig_name} 수신, 종료 중...")
        shutdown_requested = True

    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("종료하려면 Ctrl+C를 누르세요...")

    # 메인 루프 (임시 - Worker 연동 시 교체 예정)
    while not shutdown_requested:
        signal.pause()  # 시그널 대기

    print("분석 레이어 종료 완료")
    sys.exit(0)


if __name__ == "__main__":
    main()
