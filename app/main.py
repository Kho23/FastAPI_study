from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine, SessionLocal
from app.core.exceptions import register_exception_handlers
from app.imports.router import router as import_router
from app.transactions import models
from app.transactions.router import router as transaction_router
from app.categories.router import router as category_router
from app.categories.service import seed_defaults

from pathlib import Path
from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine) # 서버 시작 시 1회 실행
    with SessionLocal() as db:
        seed_defaults(db)
    yield
    # 아래부터는 서버 종료 시 실행

app = FastAPI(lifespan=lifespan)
app.include_router(import_router)
app.include_router(transaction_router)
app.include_router(category_router)

register_exception_handlers(app)

app.mount("/ui", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="ui")