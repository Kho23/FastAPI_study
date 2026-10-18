from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.categories.models import Category, CategoryRule

def list_categories(db: Session) -> list[Category]:
    stmt = select(Category).options(selectinload(Category.rules)).order_by(Category.id)
    return db.scalars(stmt).all()

def get_category(db: Session, category_id: int) -> Category | None:
    return db.get(Category, category_id)

def find_category_by_name(db: Session, name: str) -> Category | None:
    return db.scalar(select(Category).where(Category.name == name))

def find_rule_by_keyword(db: Session, keyword: str) -> CategoryRule | None:
    return db.scalar(select(CategoryRule).where(CategoryRule.keyword == keyword))

def list_rules(db: Session) -> list[CategoryRule]:
    stmt = select(CategoryRule).options(selectinload(CategoryRule.category))
    return db.scalars(stmt).all()

def add_category(db: Session, name: str) -> Category:
    category = Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def add_rule(db: Session, category: Category, keyword: str) -> CategoryRule:
    rule = CategoryRule(keyword=keyword, category=category)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule