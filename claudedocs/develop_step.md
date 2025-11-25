# 분석 레이어 개발 단계

데이터 흐름 순서에 따라 점진적으로 개발합니다. 각 단계는 해당 단계에 필요한 작업만 수행합니다.

---

## 데이터 흐름
```
main.py
  ↓
인프라 컴포넌트 생성 (MessageSubscriber, Database, MessagePublisher)
  ↓
Worker(message_subscriber, llm_service, database, message_publisher)
  ↓
Worker.run() (무한 루프)
  ├─ MessageSubscriber.receive()   ← 메시지 수신 (blocking)
  ├─ LLMService.analyze(raw_data)  ← LLM 분석
  ├─ Database.save(analysis_result) ← 결과 저장
  ├─ MessagePublisher.publish()     ← 다음 레이어로 발행
  └─ MessageSubscriber.ack()        ← 처리 완료
```

---

## Step 1: 진입점 생성

**목적:** 애플리케이션 시작점 마련

**작업:**
- `main.py` 파일 생성
- SIGINT/SIGTERM 시그널 핸들링 (우아한 종료)

**확인:**
- `python main.py` 실행 및 Ctrl+C 종료 확인

---

## Step 2: 구조화된 로깅 추가

**목적:** 실행 흐름 및 에러 추적

**작업:**
- `src/logger.py` 모듈 생성
- `main.py`에서 logger 사용

**확인:**
- 로그 출력 확인

---

## Step 3: Worker 기본 골격

**목적:** 메시지 처리 루프 구조 마련

**작업:**
- `src/worker.py` 생성
- Worker 클래스 정의
  - `run()`: 무한 루프 (빈 구현, sleep으로 대기)
  - `shutdown()`: 종료 플래그
- `main.py`에서 Worker 생성 및 실행

**확인:**
- Worker 실행 로그 확인

---

## Step 4: MessageSubscriber 구현

**목적:** Redis Streams에서 메시지 수신

**작업:**
- `src/infrastructure/message_subscriber.py` 생성
  - 스트림: `trump-scan:data-collection:raw-data`
  - Consumer Group: `analysis-workers`
  - `receive()`: XREADGROUP (blocking)
  - `ack(message_id)`: 처리 완료
- `config/redis.py` 생성
- `src/models/raw_data.py` 생성 (메시지 파싱에 필요)
- Worker에서 MessageSubscriber.receive() 호출

**확인:**
- redis-cli로 XADD 후 메시지 수신 확인

---

## Step 5: LLMService 구현

**목적:** Gemini API 호출 및 응답 처리

**작업:**
- `src/services/prompt_builder.py` 생성
  - `build(raw_data) -> str`
- `src/services/llm_service.py` 생성
  - `analyze(raw_data) -> AnalysisResult`
  - 재시도 로직 (타임아웃, Rate Limit)
- `src/models/analysis_result.py` 생성 (LLM 응답 구조화에 필요)
- `config/llm.py` 생성 (API 키, 모델명)
- Worker에서 LLMService.analyze() 호출
- 테스트 작성

**확인:**
- Gemini API 호출 및 응답 파싱 확인

---

## Step 6: Database 구현

**목적:** 분석 결과 저장

**작업:**
- `src/infrastructure/database.py` 생성
  - `save_analysis_result(result) -> AnalysisResult`
- `sql/ddl.sql` 생성
- `config/database.py` 생성
- Worker에서 Database.save() 호출

**확인:**
- DB 저장 및 ID 할당 확인

---

## Step 7: MessagePublisher 구현

**목적:** 다음 레이어로 데이터 전달

**작업:**
- `src/infrastructure/message_publisher.py` 생성
  - 스트림: `trump-scan:analysis:analysis-result`
  - `publish(result)`
- Worker에서 MessagePublisher.publish() 호출
- Worker에서 MessageSubscriber.ack() 호출

**확인:**
- redis-cli로 발행된 메시지 확인
- 전체 흐름 동작 확인

---

## 단계별 개발 원칙

1. **점진적 개발**: 각 단계는 이전 단계에 의존
2. **필요한 것만**: 해당 단계에 필요한 파일/라이브러리만 추가
3. **동작 확인**: 각 단계마다 실행하여 동작 확인
4. **커밋 단위**: 각 단계를 완료하면 커밋