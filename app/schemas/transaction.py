from pydantic import BaseModel


class DepositRequest(BaseModel):
    account_no: int
    password: str
    amount: float


class WithdrawRequest(BaseModel):
    account_no: int
    password: str
    amount: float


class TransferRequest(BaseModel):
    sender_account_no: int
    password: str
    receiver_account_no: int
    amount: float


class BalanceRequest(BaseModel):
    account_no: int
    password: str


class BalanceResponse(BaseModel):
    account_no: int
    balance: float


class TransferResponse(BaseModel):
    sender_account_no: int
    receiver_account_no: int
    sender_balance: float
    receiver_balance: float
