from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine
from app.imports.router import router as import_router
from app.transactions import models
from app.transactions.router import router as transaction_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine) # 서버 시작 시 1회 실행
    yield
    # 아래부터는 서버 종료 시 실행

app = FastAPI(lifespan=lifespan)
app.include_router(import_router)
app.include_router(transaction_router)