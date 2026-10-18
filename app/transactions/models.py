from datetime import date, datetime, time

from sqlalchemy import ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.categories.models import Category
from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions" # DB 테이블명
    __table_args__ = ( # 테이블 전체 옵션 설정
        UniqueConstraint( # 아래 3개 값의 조합이 Unique 해야 한다.(PK와 다른 개념)
            "source", "approval_no", "transacted_at",
            name="uq_transactions_source_approval"
        ),
    )
    # Mapped[타입] : 이 속성은 DB 컬럼이라는 의미이다.
    # Mapped[str] 은 Not Null
    # mapped_column 은 속성 옵션을 추가할 때 사용(없으면 생략)
    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(20))
    transacted_at : Mapped[date]
    transacted_time : Mapped[time | None] # | None 은 nullable
    merchant: Mapped[str]
    amount : Mapped[int]
    discount: Mapped[int] = mapped_column(default=0)
    payment_type : Mapped[str | None]
    status: Mapped[str]
    card_name: Mapped[str | None]
    approval_no : Mapped[str]
    created_at : Mapped[datetime] = mapped_column(server_default=func.now()) # 값이 없으면 현재 시간
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category | None"] =  relationship()