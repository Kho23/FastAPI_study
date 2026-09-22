from datetime import date

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.transactions.models import Transaction

def find_existing_keys(db: Session, source: str) -> set[tuple[str, date]]:
    """저장된 거래 승인번호, 이용일 목록을 가져옴. 중복 판별용"""
    # select, where 은 파이썬 코드로 쿼리를 조립
    stmt = select(Transaction.approval_no, Transaction.transacted_at).where(
        Transaction.source == source
    )
    """
    == select approval_no, transacted_at from Transaction where Transaction.source == 매개변수 source
    """
    return {(approval_no, transacted_at) for approval_no, transacted_at in db.execute(stmt)}

def add_all(db:Session, transactions: list[Transaction]) -> None:
    db.add_all(transactions)
    db.commit()

def search(
    db: Session,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    merchant: str | None = None,
    source: str | None = None,
    offset: int = 0,
    limit: int = 20,
) -> tuple[list[Transaction], int]:
    """조건에 맞는 거래 목록과 전체 건수를 돌려준다."""
    stmt = select(Transaction)
    # where 조건문에 맞는 데이터만 조회하도록 설정
    if start_date is not None:
        stmt = stmt.where(Transaction.transacted_at >= start_date)
    if end_date is not None:
        stmt = stmt.where(Transaction.transacted_at<=end_date)
    if merchant:
        stmt = stmt.where(Transaction.merchant.contains(merchant))
    if source:
        stmt = stmt.where(Transaction.source == source)
    # scalar 는 각 행의 첫번째 값만 가져옴 cur.fetchone() 과 같음
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))

    stmt = stmt.order_by(
        Transaction.transacted_at.desc(),
        Transaction.transacted_time.desc(),
        Transaction.id.desc()
    )
    items = db.scalars(stmt.offset(offset).limit(limit)).all()
    return items, total

def get_by_id(db: Session, transaction_id: int) -> Transaction | None:
    return db.get(Transaction, transaction_id)