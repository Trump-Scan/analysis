"""
데이터베이스 서비스

Oracle DB에 분석 결과를 저장합니다.
"""

import json

import oracledb

from config.database import DB_CONFIG
from src.logger import get_logger
from src.models.analysis_data import AnalysisData
from src.models.analysis_result import AnalysisResult

logger = get_logger("database")


class Database:
    """
    Oracle 데이터베이스 서비스

    분석 결과를 저장합니다.
    """

    def __init__(self):
        username = DB_CONFIG["username"]
        password = DB_CONFIG["password"]
        dsn = DB_CONFIG["dsn"]
        wallet_location = DB_CONFIG["wallet_location"]
        wallet_password = DB_CONFIG["wallet_password"]

        try:
            logger.info("Oracle DB 연결 중...", dsn=dsn)

            self._connection = oracledb.connect(
                user=username,
                password=password,
                dsn=dsn,
                config_dir=wallet_location,
                wallet_location=wallet_location,
                wallet_password=wallet_password,
            )

            logger.info("Database 연결 완료", dsn=dsn)

        except oracledb.Error as e:
            error_obj, = e.args
            logger.error(
                "DB 연결 실패",
                error_code=error_obj.code if hasattr(error_obj, "code") else None,
                error_message=str(error_obj.message) if hasattr(error_obj, "message") else str(e),
            )
            raise

    def save_analysis_data(self, raw_data_id: int, result: AnalysisResult) -> AnalysisData:
        """
        분석 데이터 저장

        Args:
            raw_data_id: 원본 데이터 ID
            result: LLM 분석 결과

        Returns:
            ID가 할당된 AnalysisData
        """
        try:
            cursor = self._connection.cursor()
            id_var = cursor.var(oracledb.NUMBER)

            cursor.execute(
                """
                INSERT INTO analysis_data (
                    raw_data_id, semantic_summary, display_summary, keywords, prompt_version
                ) VALUES (
                    :raw_data_id, :semantic_summary, :display_summary, :keywords, :prompt_version
                )
                RETURNING id INTO :id
                """,
                {
                    "raw_data_id": raw_data_id,
                    "semantic_summary": result.semantic_summary,
                    "display_summary": result.display_summary,
                    "keywords": json.dumps(result.keywords, ensure_ascii=False),
                    "prompt_version": result.prompt_version,
                    "id": id_var,
                },
            )

            record_id = int(id_var.getvalue()[0])
            self._connection.commit()
            cursor.close()

            analysis_data = AnalysisData(
                id=record_id,
                raw_data_id=raw_data_id,
                semantic_summary=result.semantic_summary,
                display_summary=result.display_summary,
                keywords=result.keywords,
                prompt_version=result.prompt_version,
            )

            logger.debug("분석 데이터 저장 완료", id=record_id, raw_data_id=raw_data_id)
            return analysis_data

        except oracledb.Error as e:
            self._connection.rollback()
            error_obj, = e.args
            logger.error(
                "분석 데이터 저장 실패",
                error_code=error_obj.code if hasattr(error_obj, "code") else None,
                error_message=str(error_obj.message) if hasattr(error_obj, "message") else str(e),
                raw_data_id=raw_data_id,
            )
            raise

    def close(self):
        """연결 종료"""
        self._connection.close()
        logger.info("Database 연결 종료")
