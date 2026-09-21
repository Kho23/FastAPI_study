# FastAPI_study — 개인 가계부 (FastAPI 학습 프로젝트)

이 파일은 Claude Code가 세션을 시작할 때 자동으로 읽는다. 컴퓨터를 옮겨도 맥락이 이어지도록 진행 상황과 작업 방식을 여기에 기록한다. 단계가 끝날 때마다 "진행 상황"을 갱신할 것.

## 프로젝트

- 목적: FastAPI 학습. 결과물은 KB국민카드 + 현대카드 이용내역 엑셀을 읽어 들이는 개인 가계부.
- 스택: FastAPI, SQLAlchemy 2.0(동기 세션), SQLite(`data/ledger.db`), pydantic-settings, openpyxl, pytest.
- 구조: `app/<도메인>/{router,service,repository,models,schemas}.py` — Spring의 Controller/Service/Repository/Entity/DTO에 대응.
- 실행: 프로젝트 루트에서 `fastapi dev app/main.py` (항상 루트에서 실행). 테스트는 `python -m pytest -v`.
- 디버깅: PyCharm Python 구성 — module `uvicorn`, parameters `app.main:app --port 8000`, reload 없이.

## 사용자와 작업 방식

- 사용자는 FastAPI 입문자이고 Spring/JPA 경험이 있다. 새 개념은 "왜 필요한가 → 무엇인가 → 이 프로젝트에서 어떻게 쓰는가" 순서로, Spring 대응물과 차이점을 곁들여 한국어로 설명한다.
- 영어 독해가 약해 개발 영어를 늘리고 싶어 한다. 새 용어가 나오면 답변 끝에 짧은 용어 풀이를 붙인다.
- **코드는 사용자가 직접 타이핑한다.** Claude는 코드를 제시하고 설명하며, `app/`·`tests/` 파일을 대신 수정하지 않는다.
- 사용자가 "현 상태 점검"을 요청하면 실제 파일을 읽고, 가능하면 직접 실행해서 검증한다. 오타성 버그(필드명 오타, `Depends(get_db())`의 괄호, 타입 불일치)가 자주 나온다.
- 제시하는 코드는 먼저 임시 DB로 돌려 검증한다. 실제 `data/ledger.db`에는 쓰지 않는다(읽기 전용 확인만).
- 설명이 길어지면 사용자는 "그냥 순서대로"를 선호한다. 표·비교보다 단계별 흐름 위주로.

## 진행 상황 (2026-09-21 기준)

- [x] ① DB 저장 — config → database → `Transaction` 모델 → `imports/service.py`. `(source, approval_no, transacted_at)` 유니크 제약 + 코드에서 선(先) 중복 제거.
- [x] ② 거래 조회 — `GET /transactions`(기간·가맹점·source 필터, page/size), `GET /transactions/{id}`.
- [x] ③ 업로드 전환 — `POST /imports/excel`이 `UploadFile`을 받는다. 잘못된 파일은 400.
- [ ] ④ 테스트 — `tests/conftest.py`(임시 DB로 `get_db` 교체 + 코드로 만든 가짜 KB 엑셀)와 `tests/test_imports.py` 6개 케이스를 안내함. 사용자가 입력 중.
- [ ] ⑤ 현대카드 파서 + `parsers/base.py` 공통 인터페이스. 이때 파서 전용 예외(`InvalidStatementError` 등)를 만들고 `core/exceptions.py`에서 exception handler로 일괄 처리(라우터의 `except (BadZipFile, OSError, KeyError, IndexError, ValueError)` 나열을 대체). 현대카드 실제 엑셀 샘플이 아직 없다.
- [ ] ⑥ 카테고리 자동 분류 (가맹점명 키워드 규칙) — `app/categories/`
- [ ] ⑦ 월별·카테고리별 리포트 — `app/reports/`

## 알아 둘 것

- KB 엑셀 구조: 1~6행 요약, 7행 헤더(셀 안에 줄바꿈 있음), 8행부터 데이터, 중간에 빈 행 있음. 승인번호는 중복되지 않는다.
- **취소 건(`승인취소`, `취소전표매입`)은 금액이 음수가 아니라 양수로 들어온다.** 합계·리포트에서는 `status`로 걸러야 한다. 현재 `ImportResult.total_amount`는 취소 건을 포함한 값이다.
- `create_all`은 없는 테이블만 만든다. 모델의 컬럼·테이블명을 바꾸면 `data/ledger.db`를 지우고 다시 만들어야 한다(Alembic 미도입).
- 윈도우에서 reload 서버를 비정상 종료하면 워커가 8000번 포트를 잡은 채 남는다. "고쳤는데 반영이 안 된다" 싶으면 `netstat -ano | findstr :8000`으로 LISTENING이 2개인지 확인하고 `taskkill /PID <pid> /F`.
- 회사 PC에서는 보안 프로그램이 브라우저 파일 업로드를 막아 Swagger로 업로드 테스트가 안 된다. 업로드는 pytest(`TestClient`)로 검증한다. 필요하면 경로 기반 엔드포인트(`POST /imports/excel/path`)를 추가하는 안을 제시해 두었다.
- 엔드포인트는 `def`로 선언한다(동기 SQLAlchemy·openpyxl 사용). `await`할 것이 없으면 `async def`를 쓰지 않는다.

## 개인정보

- `data/`, `*.db`, `*.xlsx`, `.env`는 `.gitignore`에 있다. 실제 카드내역·DB는 커밋하지 않는다.
- 테스트는 실제 카드내역 파일에 의존하지 않고 코드로 만든 가짜 엑셀을 쓴다.
- 문서·커밋 메시지·테스트에 실제 거래 내용(가맹점명, 금액)을 옮겨 적지 않는다.
