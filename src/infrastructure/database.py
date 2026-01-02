"""
데이터베이스 서비스

Oracle DB에 분석 결과를 저장합니다.
"""

import json

import oracledb

from config.database import DB_CONFIG
from src.logger import get_logger
from src.models.analysis_data import AnalysisData
from src.models.analysis_message import AnalysisMessage
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

    def get_latest_analysis_data(self) -> AnalysisData:
        """
        가장 최근 analysis_data 1건 조회

        Returns:
            AnalysisData 또는 None (데이터 없는 경우)
        """
        try:
            cursor = self._connection.cursor()

            cursor.execute(
                """
                SELECT id, raw_data_id, semantic_summary, display_summary, keywords, prompt_version
                FROM analysis_data
                ORDER BY id DESC
                FETCH FIRST 1 ROW ONLY
                """
            )

            row = cursor.fetchone()
            cursor.close()

            if row is None:
                return None

            db_id, raw_data_id, semantic_summary, display_summary, keywords_str, prompt_version = row

            return AnalysisData(
                id=int(db_id),
                raw_data_id=int(raw_data_id),
                semantic_summary=semantic_summary,
                display_summary=display_summary,
                keywords=json.loads(keywords_str),
                prompt_version=prompt_version,
            )

        except oracledb.Error as e:
            error_obj, = e.args
            logger.error(
                "데이터 조회 실패",
                error_code=error_obj.code if hasattr(error_obj, "code") else None,
                error_message=str(error_obj.message) if hasattr(error_obj, "message") else str(e),
            )
            raise

    def get_latest_analysis_message(self) -> AnalysisMessage:
        """
        가장 최근 analysis_data를 raw_data와 조인하여 조회

        Returns:
            AnalysisMessage 또는 None (데이터 없는 경우)
        """
        try:
            cursor = self._connection.cursor()

            cursor.execute(
                """
                SELECT
                    a.id, a.raw_data_id, a.semantic_summary, a.display_summary,
                    a.keywords, a.prompt_version,
                    r.channel, r.link, r.published_at
                FROM analysis_data a
                JOIN raw_data r ON a.raw_data_id = r.id
                ORDER BY a.id DESC
                FETCH FIRST 1 ROW ONLY
                """
            )

            row = cursor.fetchone()
            cursor.close()

            if row is None:
                return None

            (
                db_id, raw_data_id, semantic_summary, display_summary,
                keywords_str, prompt_version,
                channel, link, published_at
            ) = row

            return AnalysisMessage(
                id=int(db_id),
                raw_data_id=int(raw_data_id),
                semantic_summary=semantic_summary,
                display_summary=display_summary,
                keywords=json.loads(keywords_str),
                prompt_version=prompt_version,
                channel=channel,
                original_link=link,
                published_at=published_at,
            )

        except oracledb.Error as e:
            error_obj, = e.args
            logger.error(
                "AnalysisMessage 조회 실패",
                error_code=error_obj.code if hasattr(error_obj, "code") else None,
                error_message=str(error_obj.message) if hasattr(error_obj, "message") else str(e),
            )
            raise

    def close(self):
        """연결 종료"""
        self._connection.close()
        logger.info("Database 연결 종료")
