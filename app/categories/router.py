from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.categories import repository, service
from app.categories.schemas import CategoryCreate, CategoryOut, ReclassifyResult, RuleCreate, RuleOut

from app.core.database import get_db

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("", response_model=list[CategoryOut])
def list_categories(db: Annotated[Session, Depends(get_db)]):
    return repository.list_categories(db)

@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(body: CategoryCreate, db: Annotated[Session, Depends(get_db)]):
    return service.create_category(db, body.name)

@router.post("/{category_id}/rules", response_model=RuleOut, status_code=status.HTTP_201_CREATED)
def create_rule(category_id: int, body: RuleCreate, db: Annotated[Session, Depends(get_db)]):
    return service.create_rule(db, category_id, body.keyword)

@router.post("/reclassify", response_model=ReclassifyResult)
def reclassify(db: Annotated[Session, Depends(get_db)]):
    return ReclassifyResult(updated=service.reclassify_uncategorized(db))
