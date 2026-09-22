from sqlalchemy import select
from sqlalchemy.orm import Session
from unicodedata import category

from app.categories import repository
from app.categories.classifier import classify
from app.categories.models import Category, CategoryRule
from app.core.exceptions import AppError, NotFoundError
from app.transactions.models import Transaction

DEFAULT_RULES: dict[str, list[str]] = {
    "편의점": ["GS25", "지에스25", "지에스(GS25)", "씨유", "세븐일레븐", "이마트24", "미니스톱"],
    "카페": ["커피", "카페", "CAFE", "스타벅스", "빽다방", "메가엠지씨", "컴포즈", "투썸", "이디야"],
    "간식/디저트": ["아이스크림", "배스킨라빈스", "베이커리", "파리바게뜨", "뚜레쥬르", "던킨"],
    "배달": ["쿠팡이츠", "배달의민족", "요기요"],
    "외식": ["식당", "반점", "국밥", "감자탕", "카츠",
             "버거킹", "비케이알", "맥도날드", "롯데리아", "맘스터치", "김밥", "치킨", "피자"],
    "쇼핑": ["쿠팡", "네이버페이", "무신사", "다이소", "올리브영", "교보문고"],
    "교통": ["카카오 T", "카카오T", "택시", "버스", "지하철", "코레일", "주유"],
    "의료": ["약국", "의원", "병원", "치과", "피부과"],
    "담배": ["담배", "전담"],
    "문화/여가": ["노래연습장", "노래방", "영화", "CGV", "메가박스", "놀유니버스", "PC방"],
    "보험": ["보험"],
    "공과금가계부/통신": ["공공요금", "SKT", "LG유플러스", "전기요금", "도시가스"],
    "구독": ["넷플릭스", "유튜브", "멜론", "스포티파이", "쿠팡와우"],
}

def seed_defaults(db: Session) -> None:
    """카테고리가 빈 상태면 기본 규칙 삽입"""
    if repository.list_categories(db):
        return
    for name, keywords in DEFAULT_RULES.items():
        category = Category(name=name)
        category.rules = [CategoryRule(keyword = k) for k in keywords]
        db.add(category)
    db.commit()

def create_rule(db: Session, category_id: int, keyword: str) -> CategoryRule:
    category = repository.get_category(db, category_id)
    if category is None:
        raise NotFoundError("카테고리를 찾을 수 없습니다.")
    if repository.find_rule_by_keyword(db, keyword):
         raise AppError(f"이미 있는 키워드입니다({keyword})")
    return repository.add_rule(db, category, keyword)


