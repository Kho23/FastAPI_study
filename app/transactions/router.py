from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.transactions import repository, service
from app.transactions.schemas import TransactionOut, TransactionPage, TransactionCategoryUpdate
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("", response_model=TransactionPage)
def list_transactions(
        db: Annotated[Session, Depends(get_db)],
        start_date: date | None = None,
        end_date: date | None = None,
        merchant: str | None = None,
        source: str | None = None,
        category_id: int | None = None,
        page: Annotated[int, Query(ge=1)] = 1,
        size: Annotated[int, Query(ge=1, le=100)] = 20
):
    items, total = repository.search(
        db,
        start_date=start_date,
        end_date=end_date,
        merchant=merchant,
        source=source,
        category_id=category_id,
        offset=(page - 1) * size,
        limit=size,
    )
    return TransactionPage(total=total, page=page, size=size, items=items)

@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: int, db: Annotated[Session, Depends(get_db)]):
    transaction = repository.get_by_id(db, transaction_id)
    if transaction is None:
        raise NotFoundError(detail="조회된 거래내역이 없습니다.")
    return transaction

@router.patch("/{transaction_id}", response_model=TransactionOut)
def update_transaction_category(
        transaction_id: int,
        body: TransactionCategoryUpdate,
        db: Annotated[Session, Depends(get_db)]
):
    return service.update_category(db, transaction_id, body.category_id)