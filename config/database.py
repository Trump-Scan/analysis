"""
데이터베이스 설정

환경변수 기반으로 설정값을 주입합니다.
"""

import os

# Oracle Database 설정
DB_CONFIG = {
    "username": os.environ.get("DB_USERNAME", "YOUR_USERNAME"),
    "password": os.environ.get("DB_PASSWORD", "YOUR_PASSWORD"),
    "dsn": os.environ.get("DB_DSN", "YOUR_DSN"),
    "wallet_location": os.environ.get("DB_WALLET_LOCATION", "/path/to/wallet/directory"),
    "wallet_password": os.environ.get("DB_WALLET_PASSWORD", "YOUR_WALLET_PASSWORD"),
}
