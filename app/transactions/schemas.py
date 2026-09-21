from datetime import date, time

from pydantic import BaseModel, ConfigDict

class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id : int
    source : str
    transacted_at : date
    transacted_time : time | None
    merchant : str
    amount : int
    discount : int
    payment_type : str | None
    status : str
    card_name : str | None
    approval_no : str

class TransactionPage(BaseModel):
    total : int
    page : int
    size : int
    items : list[TransactionOut]