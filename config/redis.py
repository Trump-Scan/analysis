"""
Redis 설정

Redis Streams 연결에 필요한 설정값입니다.
"""

# Redis 연결 설정
HOST = "localhost"
PORT = 6379
DB = 0

# 스트림 설정
INPUT_STREAM = "trump-scan:data-collection:raw-data"
OUTPUT_STREAM = "trump-scan:analysis:analysis-result"
CONSUMER_GROUP = "analysis-workers"
CONSUMER_NAME = "worker-1"

# 타임아웃 설정 (밀리초)
BLOCK_TIMEOUT = 5000  # 5초
