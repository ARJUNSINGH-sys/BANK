from pydantic import BaseModel


class DepositRequest(BaseModel):
    account_no: int
    password: str
    amount: float
    reference: str | None = "Cash Deposit"


class WithdrawRequest(BaseModel):
    account_no: int
    password: str
    amount: float
    reference: str | None = "Cash Withdrawal"


class TransferRequest(BaseModel):
    sender_account_no: int
    password: str
    receiver_account_no: int
    amount: float
    reference: str | None = "Account Transfer"


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


class TransactionItemResponse(BaseModel):
    id: int
    account_no: int
    type: str
    amount: float
    receiver_account: int | None = None
    reference: str = ""
    timestamp: str


class MetricsResponse(BaseModel):
    total_customers: int
    active_accounts: int
    todays_transfers: int
    total_balance: float
