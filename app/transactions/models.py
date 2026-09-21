from datetime import date, datetime, time

from sqlalchemy import String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        UniqueConstraint(
            "source", "approval_no", "transacted_at",
            name="uq_transactions_source_approval"
        ),
    )
    # Mapped[타입] : 이 속성은 DB 컬럼이라는 의미이다.
    # Mapped[str] 은 Not Null
    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(20))
    transacted_at : Mapped[date]
    transacted_time : Mapped[time | None]
    merchant: Mapped[str]
    amount : Mapped[int]
    discount: Mapped[int] = mapped_column(default=0)
    payment_type : Mapped[str | None]
    status: Mapped[str]
    card_name: Mapped[str | None]
    approval_no : Mapped[str]
    created_at : Mapped[datetime] = mapped_column(server_default=func.now())