from sqlalchemy.orm import Session

from app.imports.parsers.kookmin import ParsedTransaction
from app.transactions import repository
from app.transactions.models import Transaction

def to_model(source: str, t: ParsedTransaction) -> Transaction:
    """등록한 엑셀을 파싱하여 DB 모델(Transaction)로 변환한다"""
    return Transaction(
        source = source,
        transacted_at = t.transacted_at,
        transacted_time = t.transacted_time,
        merchant = t.merchant,
        amount = t.amount,
        discount = t.discount,
        payment_type = t.payment_type,
        status = t.status,
        card_name = t.card_name,
        approval_no = t.approval_no
    )

def save_transactions(db: Session, source: str, parsed: list[ParsedTransaction]) -> tuple[int, int]:
    """새 거래만 저장하고, 저장 건 수와 중복 건 수를 반환"""
    seen = repository.find_existing_keys(db, source)
    new_transactions = []
    for t in parsed:
        key = (t.approval_no, t.transacted_at)
        if key in seen:
            continue
        seen.add(key)
        new_transactions.append(to_model(source, t))
    repository.add_all(db, new_transactions)
    return len(new_transactions), len(parsed)-len(new_transactions)