from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app

HEADERS = [
    "이용일", "이용 시간", "이용 고객명", "이용카드명", "이용하신곳",
    "국내이용금액\n(원)", "해외이용금액\n($)", "결제방법", "가맹점 정보",
    "할인금액", "적립(예상)\n포인트리", "상태", "결제예정일", "승인번호",
]

def make_row(day: str, merchant: str, amount: int, approval_no: str, status: str = "전표매입") -> list:
    return [day, "12:30", "홍길동", "테스트체크카드", merchant, amount, 0, "일시불", None, 0, 0, status, None, approval_no]

@pytest.fixture
def client(tmp_path):
    """임시 폴더 DB 를 사용하는 테스트용 클라이언트"""
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'test.db').as_posix()}",
        connect_args={'check_same_thread':False},
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    engine.dispose()

@pytest.fixture
def kookmin_xlsx()->BytesIO:
    """KB 국민카드 거래내역 테스트용 데이터"""
    wb = Workbook()
    ws = wb.active
    for _ in range(6):
        ws.append(["요약"])
    ws.append(HEADERS)
    # 승인 취소, 빈 행을 제대로 건너뛰는지 테스트
    ws.append(make_row("2026-09-01", "테스트커피", 4500, "10000001"))
    ws.append(make_row("2026-09-02", "테스트마트", 32000, "10000002"))
    ws.append([])
    ws.append(make_row("2026-09-03", "테스트식당", 9000, "10000003", status="승인취소"))

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer