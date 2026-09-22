from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# DB 연결을 만들어주는 엔진
engine = create_engine(
    settings.database_url,
    # 연결을 만든 쓰레드만 쓰도록 제한하는 옵션을 끔
    # FastAPI 는 요청마다 다른 쓰레드를 쓸 수도 있음
    connect_args = {"check_same_thread": False}
)

# 호출할 때마다 세 세션을 하나씩 만들어줌
SessionLocal = sessionmaker(bind = engine)

# 모든 테이블 클래스의 부모 클래스
# 이 클래스를 다시 상속하는 클래스는 DB 테이블이 된다
class Base(DeclarativeBase):
    pass

# 요청 하나당 세션 대여 후 끝나면 반납받는 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()