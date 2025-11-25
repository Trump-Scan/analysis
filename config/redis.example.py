"""
Redis 설정 템플릿

이 파일을 복사하여 redis.py로 저장하고 환경에 맞게 수정하세요.
"""

# Redis 연결 설정
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# 스트림 설정
INPUT_STREAM = "trump-scan:data-collection:raw-data"
OUTPUT_STREAM = "trump-scan:analysis:analysis-result"
CONSUMER_GROUP = "analysis-workers"
CONSUMER_NAME = "worker-1"

# 타임아웃 설정 (밀리초)
BLOCK_TIMEOUT = 5000  # 5초
