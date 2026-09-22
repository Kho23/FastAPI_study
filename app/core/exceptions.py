from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """이 앱에서 던지는 모든 예외 관리 클래스"""

    status_code = 400

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail

class InvalidStatementError(AppError):
    """카드 이용내역 엑셀이 각 카드사 엑셀 형식에 맞지 않을 때"""
    status_code = 400

class NotFoundError(AppError):
    "엑셀 파일을 발견하지 못했을 때"
    status_code = 404

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    def handle_app_error(request: Request, exc: AppError):
        return JSONResponse(status_code=exc.status_code, content={'detail': exc.detail})