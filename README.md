# 분석 레이어 (Analysis Layer)

트럼프 스캔 서비스의 분석 레이어입니다. 수집된 원본 데이터를 LLM으로 분석하여 한국어 요약과 키워드를 추출합니다.

---

## 📋 프로젝트 개요

### 목적
데이터 수집 레이어에서 전달받은 원본 데이터를 LLM(Gemini 2.0 Flash)으로 분석하여 사용자에게 제공할 수 있는 형태로 가공합니다.

### 핵심 책임
- 메시지 큐에서 원본 데이터 수신
- LLM 호출로 분석 수행 (1회 호출로 모든 항목 생성)
  - 중복 제거용 영어 요약 (Semantic Summary)
  - 사용자용 한국어 요약 (Display Summary)
  - 키워드 목록 (Keywords)
- 분석 결과 저장 (Oracle DB)
- 다음 레이어(중복 제거)로 메시지 발행

### 처리 흐름
```
[trump-scan:data-collection:raw-data] (Consumer Group: analysis-workers)
  ↓
Worker
  ├─ MessageSubscriber.receive()  ← 메시지 수신
  ├─ LLMService.analyze()         ← LLM 분석
  ├─ Database.save()              ← 결과 저장
  ├─ MessagePublisher.publish()   ← 다음 레이어로 발행
  └─ MessageSubscriber.ack()      ← 처리 완료 확인
  ↓
[trump-scan:analysis:analysis-result]
```

### 예상 처리량
- 일일 처리: 약 120개
- 건당 처리 시간: 10-30초 (LLM 응답 시간)
- 월간 LLM 비용: 약 $1.21 (Gemini 2.0 Flash 기준)

---

## 🏗️ 패키지 구조
```
analysis/
├── src/
│   ├── services/                # 핵심 서비스
│   │   ├── __init__.py
│   │   ├── llm_service.py      # LLM API 호출 및 응답 처리
│   │   └── prompt_builder.py   # 프롬프트 생성
│   │
│   ├── infrastructure/          # 인프라 레이어
│   │   ├── __init__.py
│   │   ├── message_subscriber.py  # Redis Streams 구독
│   │   ├── message_publisher.py   # Redis Streams 발행
│   │   └── database.py            # Oracle DB 연결
│   │
│   ├── models/                  # 데이터 모델
│   │   ├── __init__.py
│   │   ├── raw_data.py         # 입력 데이터 모델
│   │   └── analysis_result.py  # 분석 결과 모델
│   │
│   ├── worker.py               # 메인 워커 (흐름 조율)
│   └── logger.py               # 구조화된 로깅 설정
│
├── config/                      # 설정 파일
│   ├── __init__.py
│   ├── database.py             # DB 설정 (gitignore)
│   ├── database.example.py     # DB 설정 템플릿
│   ├── redis.py                # Redis 설정 (gitignore)
│   ├── redis.example.py        # Redis 설정 템플릿
│   ├── llm.py                  # LLM API 설정 (gitignore)
│   └── llm.example.py          # LLM API 설정 템플릿
│
├── sql/                         # 데이터베이스 스키마
│   └── ddl.sql                 # 테이블 생성 SQL
│
├── tests/                       # 테스트
│   └── __init__.py
│
├── requirements.txt
└── main.py                     # 진입점
```

### 주요 컴포넌트 설명

#### `services/`
- **`llm_service.py`**: LLM API 호출 및 응답 처리
  - Gemini 2.0 Flash API 호출
  - JSON 응답 파싱 및 검증
  - 재시도 로직 (타임아웃, Rate Limit)
- **`prompt_builder.py`**: 프롬프트 생성
  - 시스템 메시지 + 분석 지침 + 출력 형식 구성
  - 원본 데이터를 프롬프트에 포함

#### `infrastructure/`
- **`message_subscriber.py`**: Redis Streams 구독
  - 스트림: `trump-scan:data-collection:raw-data`
  - Consumer Group: `analysis-workers`
  - 메시지 수신 (XREADGROUP) 및 ACK 처리
- **`message_publisher.py`**: Redis Streams 발행
  - 스트림: `trump-scan:analysis:analysis-result`
  - 분석 완료 메시지를 다음 레이어로 발행
- **`database.py`**: Oracle DB 연결
  - 분석 결과 저장

#### `models/`
- **`raw_data.py`**: 입력 데이터 모델
  - 데이터 수집 레이어에서 전달받는 구조
- **`analysis_result.py`**: 분석 결과 모델
  - semantic_summary: 중복 제거용 영어 요약
  - display_summary: 사용자용 한국어 요약
  - keywords: 핵심 키워드 목록
  - model_name: 사용된 LLM 모델명

#### `worker.py`
- **책임**: 전체 처리 흐름 조율
  - MessageSubscriber로 메시지 수신
  - LLMService로 분석
  - Database로 저장
  - MessagePublisher로 발행
  - 에러 처리 및 우아한 종료

---

## 🛠️ 기술 스택

### 언어 및 런타임
- **Python 3.11+**

### 핵심 라이브러리

| 라이브러리 | 용도 | 버전 |
|-----------|------|------|
| **httpx** | Gemini API 호출 | >=0.24.0 |
| **pydantic** | 데이터 검증 및 모델링 | >=2.0.0 |
| **tenacity** | 재시도 로직 | >=8.0.0 |
| **redis** | Redis Streams | >=5.0.0 |
| **oracledb** | Oracle DB 연결 | >=2.0.0 |
| **structlog** | 구조화된 로깅 | >=23.0.0 |
| **pytest** | 테스팅 | >=7.0.0 |

### 인프라 의존성

| 서비스 | 용도 |
|--------|------|
| **Redis** | Message Queue (Streams) |
| **Oracle DB** | 분석 결과 저장 |
| **Gemini API** | LLM 분석 |

---

## 📊 LLM 분석 출력

### 출력 구조
```json
{
  "semantic_summary": "Trump announces 25% tariffs on Chinese goods...",
  "display_summary": "트럼프 대통령이 중국산 제품에 25% 관세를 부과한다고 발표했습니다...",
  "keywords": ["삼성전자", "반도체", "관세", "중국"]
}
```

### 필드 설명

| 필드 | 언어 | 용도 | 제한 |
|------|------|------|------|
| `semantic_summary` | 영어 | 중복 제거용 임베딩 입력 | 1,000자 이하 |
| `display_summary` | 한국어 | 사용자 피드 표시 | 3-5 문장 |
| `keywords` | 한국어 | 피드 필터링 및 태그 표시 | 5개 이하 |