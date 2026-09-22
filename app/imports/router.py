from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import InvalidStatementError
from app.imports import service
from app.imports.parsers.kookmin import KookminParser
from app.imports.schemas import CardTransactionOut, ImportResult

router = APIRouter(prefix="/imports", tags=["imports"])

PARSERS = {"kookmin": KookminParser()}

@router.post("/{source}", response_model=ImportResult)
def import_statement(source: str, file: UploadFile, db: Annotated[Session, Depends(get_db)]):
    parser = PARSERS.get(source)
    if parser is None:
        raise InvalidStatementError(f"{source} 카드사는 지원하지 않습니다.")
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise InvalidStatementError("xlsx 파일만 등록할 수 있습니다.")

    transactions = parser.parse(file.file)
    saved, skipped = service.save_transactions(db, parser.source, transactions)

    return ImportResult(
        count=len(transactions),
        saved=saved,
        skipped=skipped,
        total_amount=sum(t.amount for t in transactions),
        transactions=[
            CardTransactionOut(transacted_at=t.transacted_at, merchant=t.merchant, amount=t.amount)
            for t in transactions
        ],
    )