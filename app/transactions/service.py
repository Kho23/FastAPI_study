from sqlalchemy.orm import Session

from app.categories import repository as category_repository
from app.core.exceptions import NotFoundError
from app.transactions import repository
from app.transactions.models import Transaction

def update_category(db: Session, transaction_id: int, category_id: int | None) -> Transaction:
    """거래 카테고리를 직접 지정하며, None 이면 미분류로 되돌림"""
    transaction = repository.get_by_id(db, transaction_id)
    if transaction is None:
        raise NotFoundError("조회된 거래내역이 없습니다.")
    if category_id is not None and category_repository.get_category(db, category_id) is None:
        raise NotFoundError("해당하는 카테고리를 찾을 수 없습니다.")
    transaction.category_id = category_id
    db.commit()
    db.refresh(transaction)
    return transaction