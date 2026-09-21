from datetime import date
from pydantic import BaseModel

class CardTransactionOut(BaseModel):
    transacted_at: date  # 거래 일자
    merchant: str        # 거래 이용자
    amount: int          # 거래 금액

class ImportResult(BaseModel):
    count: int                                # 엑셀 파싱 결과수
    saved: int                                # DB 저장된 거래 수
    skipped: int                              # 중복으로 건너뛴 거래 수
    total_amount: int
    transactions: list[CardTransactionOut]
