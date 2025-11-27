"""
MessagePublisher 테스트

DB에서 최신 데이터를 조회하여 발행합니다.
"""

from src.infrastructure.database import Database
from src.infrastructure.message_publisher import MessagePublisher
from src.logger import setup_logging, get_logger

setup_logging()
logger = get_logger("test_message_publisher")


def test_publish_latest():
    """최신 데이터 발행 테스트"""
    # DB에서 최신 데이터 조회
    database = Database()
    analysis_data = database.get_latest_analysis_data()

    if analysis_data is None:
        logger.error("analysis_data 테이블에 데이터가 없습니다.")
        database.close()
        return

    logger.info(
        "최신 데이터 조회 완료",
        id=analysis_data.id,
        raw_data_id=analysis_data.raw_data_id,
    )

    # 메시지 발행
    publisher = MessagePublisher()
    message_id = publisher.publish(analysis_data)
    logger.info("발행 완료", message_id=message_id)

    # 정리
    publisher.close()
    database.close()


if __name__ == "__main__":
    test_publish_latest()
