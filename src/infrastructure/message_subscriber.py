"""
메시지 구독자

Redis Streams에서 메시지를 수신합니다.
"""

import json
from datetime import datetime
from typing import Optional

import redis

from config import redis as redis_config
from src.logger import get_logger
from src.models.raw_data import RawData

logger = get_logger("message_subscriber")


class MessageSubscriber:
    """
    Redis Streams 메시지 구독자

    Consumer Group을 사용하여 메시지를 수신하고 ACK 처리합니다.
    """

    def __init__(self):
        self._client = redis.Redis(
            host=redis_config.HOST,
            port=redis_config.PORT,
            db=redis_config.DB,
            decode_responses=True,
        )
        self._stream = redis_config.INPUT_STREAM
        self._group = redis_config.CONSUMER_GROUP
        self._consumer = redis_config.CONSUMER_NAME
        self._block_timeout = redis_config.BLOCK_TIMEOUT

        self._ensure_consumer_group()
        logger.info(
            "MessageSubscriber 초기화 완료",
            stream=self._stream,
            group=self._group,
            consumer=self._consumer,
        )

    def _ensure_consumer_group(self):
        """Consumer Group이 없으면 생성"""
        try:
            self._client.xgroup_create(
                self._stream,
                self._group,
                id="0",
                mkstream=True,
            )
            logger.info("Consumer Group 생성", group=self._group)
        except redis.ResponseError as e:
            if "BUSYGROUP" in str(e):
                logger.debug("Consumer Group 이미 존재", group=self._group)
            else:
                raise

    def receive(self) -> Optional[RawData]:
        """
        메시지 수신 (blocking)

        Returns:
            RawData: 수신된 메시지, 타임아웃 시 None
        """
        messages = self._client.xreadgroup(
            groupname=self._group,
            consumername=self._consumer,
            streams={self._stream: ">"},
            count=1,
            block=self._block_timeout,
        )

        if not messages:
            return None

        # messages: [(stream_name, [(message_id, {field: value})])]
        stream_name, stream_messages = messages[0]
        message_id, data = stream_messages[0]

        logger.debug("메시지 수신", message_id=message_id)

        # JSON 파싱 및 RawData 변환
        raw_data = self._parse_message(message_id, data)
        return raw_data

    def _parse_message(self, message_id: str, data: dict) -> RawData:
        """메시지 데이터를 RawData로 변환"""
        # data 필드가 JSON 문자열인 경우 파싱
        if "data" in data:
            parsed = json.loads(data["data"])
        else:
            parsed = data

        # datetime 필드 변환 (Z -> +00:00 변환)
        if "published_at" in parsed and isinstance(parsed["published_at"], str):
            published_at_str = parsed["published_at"].replace("Z", "+00:00")
            parsed["published_at"] = datetime.fromisoformat(published_at_str)

        return RawData(message_id=message_id, **parsed)

    def ack(self, message_id: str):
        """
        메시지 처리 완료 확인

        Args:
            message_id: 처리 완료된 메시지 ID
        """
        self._client.xack(self._stream, self._group, message_id)
        logger.debug("메시지 ACK", message_id=message_id)

    def close(self):
        """연결 종료"""
        self._client.close()
        logger.info("MessageSubscriber 연결 종료")
