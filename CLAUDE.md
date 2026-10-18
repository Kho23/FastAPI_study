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

## 진행 상황 (2026-10-18 기준)

- [x] ① DB 저장 — config → database → `Transaction` 모델 → `imports/service.py`. `(source, approval_no, transacted_at)` 유니크 제약 + 코드에서 선(先) 중복 제거.
- [x] ② 거래 조회 — `GET /transactions`(기간·가맹점·source 필터, page/size), `GET /transactions/{id}`.
- [x] ③ 업로드 전환 — `POST /imports/excel`이 `UploadFile`을 받는다. 잘못된 파일은 400.
- [x] ④ 테스트 — `tests/conftest.py`(임시 DB로 `get_db` 교체 + 코드로 만든 가짜 KB 엑셀), `tests/test_imports.py` 6개 통과.
- [x] ⑤-a 공통 파서 인터페이스(`parsers/base.py`) + 앱 예외(`core/exceptions.py`, `register_exception_handlers`) + `POST /imports/{source}`. 테스트 9개 통과.
- [~] ⑤-b 현대카드 파서(`parsers/hyundai.py`, `HyundaiParser`) — 구현 완료, 실제 파일 업로드 성공, 커밋(2026-10-18). 구조: 0~1행 요약, 2행 헤더, 마지막 행 `총 합계 :`(break로 종료). 날짜는 엑셀 일련번호(int), 금액·할부는 `'2,000원'`·`'00개월'` 문자열, 이용 시간·상태 컬럼 없음 → `status`는 금액 부호로 유도. **남은 일:** (1) 취소 행이 원결제와 승인번호·이용일이 같아(부분 취소 포함) 중복 키 `(approval_no, transacted_at)`에 걸려 건너뛰어짐 → 키에 `amount` 추가(서비스·repository·`UniqueConstraint`, DB 재생성) 필요. 코드 수정은 끝났고 테스트 18개 통과, 아직 커밋 전. 실제 `data/ledger.db` 재생성 후 두 카드 재업로드 필요. (2) `tests/test_parsers.py`에 현대카드 테스트 작성(비어 있음).
- UI 거래 탭에 "조회 결과 전체 지출" 추가(2026-10-18): 모든 페이지를 받아 프런트에서 합산. 규칙은 KB 취소(양수+취소 상태)는 제외, 현대 취소(음수)는 상계. ⑦ 리포트 API가 생기면 그걸 쓰도록 교체. 커밋(2026-10-18).
- [x] ⑥ 카테고리 자동 분류 — `app/categories/{models,classifier,repository,service,schemas,router}.py`, `Transaction.category_id` FK + `relationship`, 기본 규칙 seed(lifespan), 업로드 시 자동 분류, `POST /categories/reclassify`(미분류만 재분류, 직접 지정은 유지), `PATCH /transactions/{id}`(수동 지정), `GET /transactions?category_id=`(목록은 `selectinload`로 N+1 방지). `tests/test_category.py` 포함 18개 통과, UI 동작 확인(2026-10-11). 커밋(2026-10-18).
- [ ] ⑦ 월별·카테고리별 리포트 — `app/reports/`

## UI

- `app/static/index.html`: 프레임워크·빌드 없는 단일 HTML UI(거래 조회/카테고리 변경, 업로드, 카테고리·규칙 관리, 재분류). `main.py`에서 `app.mount("/ui", StaticFiles(...))`로 서빙 → `http://127.0.0.1:8000/ui/`. 프런트는 학습 대상이 아니라서 Claude가 작성했다(2026-09-22). API가 바뀌면 이 파일의 `fetch` 경로도 맞춘다.
- `desktop/`: Electron 껍데기(`main.js`가 `/ui/`를 창으로 띄움). `cd desktop && npm install && npm start`. FastAPI 서버가 먼저 떠 있어야 한다. `node_modules/`는 커밋하지 않는다.

## 알아 둘 것

- KB 엑셀 구조: 1~6행 요약, 7행 헤더(셀 안에 줄바꿈 있음), 8행부터 데이터, 중간에 빈 행 있음. 승인번호는 중복되지 않는다.
- **취소 건(`승인취소`, `취소전표매입`)은 금액이 음수가 아니라 양수로 들어온다.** 합계·리포트에서는 `status`로 걸러야 한다. 현재 `ImportResult.total_amount`는 취소 건을 포함한 값이다.
- `payment_type` 표기는 카드사 공통으로 `"일시불"` / `"할부 N개월"`로 통일한다(2026-10-18 결정). KB 실제 데이터는 현재 `일시불`·`포인트리`만 있어 변경 불필요. KB 할부 건이 생기면 그때 같은 표기로 맞춘다.
- `create_all`은 없는 테이블만 만든다. 모델의 컬럼·테이블명을 바꾸면 `data/ledger.db`를 지우고 다시 만들어야 한다(Alembic 미도입).
- 윈도우에서 reload 서버를 비정상 종료하면 워커가 8000번 포트를 잡은 채 남는다. "고쳤는데 반영이 안 된다" 싶으면 `netstat -ano | findstr :8000`으로 LISTENING이 2개인지 확인하고 `taskkill /PID <pid> /F`.
- 회사 PC에서는 보안 프로그램이 브라우저 파일 업로드를 막아 Swagger로 업로드 테스트가 안 된다. 업로드는 pytest(`TestClient`)로 검증한다. 필요하면 경로 기반 엔드포인트(`POST /imports/excel/path`)를 추가하는 안을 제시해 두었다.
- 엔드포인트는 `def`로 선언한다(동기 SQLAlchemy·openpyxl 사용). `await`할 것이 없으면 `async def`를 쓰지 않는다.

## 개인정보

- `data/`, `*.db`, `*.xlsx`, `.env`는 `.gitignore`에 있다. 실제 카드내역·DB는 커밋하지 않는다.
- 테스트는 실제 카드내역 파일에 의존하지 않고 코드로 만든 가짜 엑셀을 쓴다.
- `data/ledger.db`(실제 거래)가 첫 커밋부터 들어가 공개 저장소에 올라갔었다(2026-10-10 발견, 비공개 전환). 2026-10-18 `git filter-branch`로 전체 히스토리에서 `data/ledger.db`, `*.pyc`, `DEFAULT_RULES`의 개인 단골 가게 키워드를 지우고 force push했다. 이때 모든 커밋 해시가 바뀌었다. 공개 기간에 이미 복제됐을 가능성은 되돌릴 수 없다.
- `categories/service.py`의 `DEFAULT_RULES`에는 프랜차이즈 등 일반 키워드만 둔다. 개인 단골 가게는 UI의 규칙 추가로 넣어 DB에만 저장한다.
- 문서·커밋 메시지·테스트에 실제 거래 내용(가맹점명, 금액)을 옮겨 적지 않는다.
