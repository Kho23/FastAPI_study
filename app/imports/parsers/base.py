from dataclasses import dataclass
from datetime import date, time
from typing import IO, Protocol

@dataclass
class ParsedTransaction:
    """카드사 상관없이 공통 거래형태. DB가 받는 형태는 하나로 통일되어야 한다."""
    transacted_at: date
    transacted_time: time | None
    merchant: str
    amount: int
    discount: int
    payment_type: str | None
    status: str
    card_name: str | None
    approval_no: str

class StatementParser(Protocol):
    """카드사 별 파서의 틀. 구현 클래스가 상속할 필요는 없음"""
    source: str

    def parse(self, file: IO[bytes]) -> list[ParsedTransaction]: ...
