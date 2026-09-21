"""KB국민카드 이용내역 엑셀 파서.

KB국민카드 홈페이지에서 내려받은 '카드이용내역' xlsx 파일을 읽어
거래 한 건당 하나의 CardTransaction 객체로 변환한다.

파일 구조 (2026-09 기준):
    - 1~6행: 조회기간, 카드번호, 정상/취소 건수·금액 요약. 파싱하지 않는다.
    - 7행:   컬럼 헤더 (이용일, 이용 시간, 이용하신곳, ...)
    - 8행~:  거래 데이터. 빈 행은 건너뛴다.

이 모듈은 DB나 FastAPI를 전혀 알지 못한다. 파일 경로를 받아
파이썬 객체 목록을 돌려주는 순수 변환 계층이다.
"""

from openpyxl import load_workbook
from dataclasses import dataclass
from datetime import date, time, datetime

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"

@dataclass
class CardTransaction:
    """카드 거래 한 건.

    엑셀의 한 행이 이 객체 하나에 대응한다. 필드 이름은 엑셀 컬럼명이
    아니라 의미 기준으로 정했고, 값은 이미 타입 변환이 끝난 상태다.
    즉 이 객체를 받는 쪽은 날짜 형식이나 쉼표 같은 원본 표기를
    신경 쓸 필요가 없다.

    Attributes:
        transacted_at: 이용일.
        transacted_time: 이용 시간.
        customer_name: 이용 고객명.
        card_name: 이용카드명.
        merchant: 이용하신곳(가맹점명).
        amount: 국내이용금액(원).
        foreign_amount: 해외이용금액($). 국내 거래는 0.
        payment_type: 결제방법. 일시불, 할부 등.
        merchant_note: 가맹점 정보. 대부분 비어 있다.
        discount: 할인금액.
        points: 적립(예상) 포인트리.
        status: 상태. 전표매입 등.
        billing_date: 결제예정일. 체크카드는 비어 있다.
        approval_no: 승인번호. 계산 대상이 아니라 문자열로 둔다.
    """

    transacted_at: date
    transacted_time: time
    customer_name: str
    card_name: str
    merchant: str
    amount: int
    foreign_amount: int
    payment_type: str
    merchant_note: str | None
    discount: int
    points: int
    status: str
    billing_date: date | None
    approval_no: str

def open_excel(file)->list[CardTransaction]:
    """엑셀 파일을 읽어 거래 목록으로 변환한다.

    처리 순서:
        1. 첫 번째 시트의 모든 행을 값만 꺼내 리스트로 읽는다.
        2. 헤더 행을 찾아 컬럼명을 정리한다. 헤더 셀에 줄바꿈이
           섞여 있어 공백으로 바꾼다.
        3. 헤더 아래 행마다 {컬럼명: 값} 딕셔너리를 만들고
           to_dataclass로 CardTransaction으로 바꾼다.
        4. 완전히 빈 행은 건너뛴다.

    Args:
        file: 읽을 xlsx 파일.

    Returns:
        거래 한 건당 CardTransaction 하나씩 담긴 리스트.
    """
    if not file:
        raise ValueError(".")
    ws = load_workbook(file).active
    rows = list(ws.iter_rows(values_only=True))
    header_idx = 6 # 헤더 인덱스
    headers = [str(c).replace("\n", " ").strip() for c in rows[header_idx]]
    card_transaction = []
    for row in rows[header_idx+1:]:
        if all(c is None for c in row):
            continue
        record = dict(zip(headers, row))
        card_transaction.append(to_dataclass(record))
    return card_transaction

def parse_date(value) -> date | None:
    """엑셀 셀 값을 date로 바꾼다.

    openpyxl은 같은 날짜 컬럼이라도 파일에 따라 문자열("2026-09-03")로
    주기도 하고 datetime 객체로 주기도 한다. 두 경우를 모두 받아
    date 하나로 통일한다.

    Args:
        value: 셀 값. None, 빈 문자열, 날짜 문자열, datetime 중 하나.

    Returns:
        변환된 date. 값이 비어 있으면 None.
    """
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    return datetime.strptime(str(value).strip(), DATE_FORMAT).date()


def parse_time(value) -> time | None:
    """엑셀 셀 값을 time으로 바꾼다.

    parse_date와 같은 이유로 문자열("14:05")과 datetime 객체를
    모두 받아 time 하나로 통일한다.

    Args:
        value: 셀 값. None, 빈 문자열, 시각 문자열, datetime 중 하나.

    Returns:
        변환된 time. 값이 비어 있으면 None.
    """
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.time()
    return datetime.strptime(str(value).strip(), TIME_FORMAT).time()


def to_dataclass(record: dict) -> CardTransaction:
    """엑셀 한 행(딕셔너리)을 CardTransaction으로 바꾼다.

    이 함수가 엑셀 컬럼명과 CardTransaction 필드를 잇는 유일한 지점이다.
    카드사가 컬럼명을 바꾸면 여기만 고치면 된다. q

    변환 규칙:
        - 날짜·시간은 parse_date, parse_time으로 타입을 맞춘다.
        - 금액 계열은 빈 셀이면 0으로 본다.
        - 비어 있을 수 있는 컬럼은 record.get으로 읽어 키가 없어도
          에러가 나지 않게 한다.
        - 승인번호는 앞자리 0이 사라지지 않도록 문자열로 둔다.

    Args:
        record: {엑셀 컬럼명: 셀 값} 형태의 딕셔너리. 키는 open_excel에서
            줄바꿈과 공백을 정리한 헤더명이다.

    Returns:
        타입 변환이 끝난 CardTransaction.
    """
    return CardTransaction(
        transacted_at=parse_date(record["이용일"]),
        transacted_time=parse_time(record["이용 시간"]),
        customer_name=record["이용 고객명"],
        card_name=record["이용카드명"],
        merchant=record["이용하신곳"],
        amount=int(record["국내이용금액 (원)"] or 0),
        foreign_amount=int(record["해외이용금액 ($)"] or 0),
        payment_type=record["결제방법"],
        merchant_note=record.get("가맹점 정보"),
        discount=int(record["할인금액"] or 0),
        points=int(record["적립(예상) 포인트리"] or 0),
        status=record["상태"],
        billing_date=parse_date(record.get("결제예정일")),
        approval_no=str(record["승인번호"]),
    )
