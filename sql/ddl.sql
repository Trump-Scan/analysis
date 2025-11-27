-- 분석 데이터 테이블
CREATE TABLE analysis_data (
    -- 기본 키
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- 참조 필드
    raw_data_id NUMBER NOT NULL,        -- 원본 데이터 ID (raw_data.id 참조)

    -- 분석 결과 필드
    semantic_summary VARCHAR2(1000) NOT NULL,   -- 중복 제거용 영어 요약
    display_summary VARCHAR2(2000) NOT NULL,    -- 사용자용 한국어 요약
    keywords VARCHAR2(500) NOT NULL,            -- 키워드 목록 (JSON 배열)
    prompt_version VARCHAR2(20) NOT NULL,       -- 프롬프트 버전

    -- 메타 데이터
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 인덱스 생성
CREATE INDEX idx_analysis_data_raw_data_id ON analysis_data(raw_data_id);
CREATE INDEX idx_analysis_data_created_at ON analysis_data(created_at);

-- 테이블 코멘트
COMMENT ON TABLE analysis_data IS 'LLM 분석 결과 데이터';
COMMENT ON COLUMN analysis_data.id IS '분석 결과 고유 ID (자동 생성)';
COMMENT ON COLUMN analysis_data.raw_data_id IS '원본 데이터 ID (raw_data.id 참조)';
COMMENT ON COLUMN analysis_data.semantic_summary IS '중복 제거용 영어 요약 (임베딩 유사도 비교용)';
COMMENT ON COLUMN analysis_data.display_summary IS '사용자용 한국어 요약';
COMMENT ON COLUMN analysis_data.keywords IS '핵심 키워드 목록 (JSON 배열)';
COMMENT ON COLUMN analysis_data.prompt_version IS '분석에 사용된 프롬프트 버전';
COMMENT ON COLUMN analysis_data.created_at IS '분석 결과 생성 시간';
