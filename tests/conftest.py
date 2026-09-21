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
    return [day, ]