from typing import Annotated
from zipfile import BadZipFile

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.imports import service
from app.imports.parsers.kookmin import open_excel
from app.imports.schemas import CardTransactionOut, ImportResult

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/excel", response_model=ImportResult)
def import_excel(file: UploadFile, db:Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="xlsx 확장자 파일이 아닙니다.")
    try:
        transactions = open_excel(file.file)
    except (BadZipFile, OSError, KeyError, IndexError, ValueError):
        raise HTTPException(status_code = 400, detail="KB국민카드 이용내역 형식이 아닙니다.")

    saved, skipped = service.save_transactions(db, 'kookmin', transactions)
    return ImportResult(
        count=len(transactions),
        saved=saved,
        skipped=skipped,
        total_amount=sum(t.amount for t in transactions),
        transactions=[
            CardTransactionOut(
                transacted_at=t.transacted_at,
                merchant=t.merchant,
                amount=t.amount,
            )
            for t in transactions
        ],
    )