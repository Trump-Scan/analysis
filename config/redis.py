"""
Redis 설정

환경변수 기반으로 연결 설정을 주입합니다.
"""

import os

# Redis 설정
REDIS_CONFIG = {
    "host": os.environ.get("REDIS_HOST", "localhost"),
    "port": int(os.environ.get("REDIS_PORT", "6379")),
    "db": int(os.environ.get("REDIS_DB", "0")),
    "input_stream": "trump-scan:data-collection:raw-data",
    "output_stream": "trump-scan:analysis:analysis-result",
    "consumer_group": "analysis-workers",
    "consumer_name": os.environ.get("CONSUMER_NAME", "worker-1"),
    "block_timeout": 5000,
}
