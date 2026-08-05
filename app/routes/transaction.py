from fastapi import APIRouter, HTTPException, Query
from ..schemas.transaction import (
    BalanceRequest,
    BalanceResponse,
    DepositRequest,
    TransferRequest,
    TransferResponse,
    WithdrawRequest,
    TransactionItemResponse,
    MetricsResponse,
)
from ..services.transaction_service import TransactionService
from ..services.auth_service import AuthService

router = APIRouter(prefix="/transactions", tags=["transactions"])
service = TransactionService()
auth = AuthService()


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    return service.get_metrics()


@router.get("/history", response_model=list[TransactionItemResponse])
async def get_all_history(limit: int = Query(default=50, ge=1, le=200)):
    return service.get_history(account_no=None, limit=limit)


@router.get("/history/{account_no}", response_model=list[TransactionItemResponse])
async def get_account_history(account_no: int, limit: int = Query(default=50, ge=1, le=200)):
    return service.get_history(account_no=account_no, limit=limit)


@router.post("/balance", response_model=BalanceResponse)
async def get_balance(payload: BalanceRequest):
    if not auth.login(payload.account_no, payload.password):
        raise HTTPException(status_code=401, detail="Unauthorized: invalid account or password")
    current_balance = service.get_balance(payload.account_no, payload.password)
    if current_balance is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"account_no": payload.account_no, "balance": current_balance}


@router.post("/deposit", response_model=BalanceResponse)
async def deposit(payload: DepositRequest):
    if not auth.login(payload.account_no, payload.password):
        raise HTTPException(status_code=401, detail="Unauthorized: invalid account or password")
    ref = payload.reference or "Cash Deposit"
    new_balance = service.deposit(payload.account_no, payload.password, payload.amount, reference=ref)
    if new_balance is None or new_balance is False:
        raise HTTPException(status_code=400, detail="Invalid deposit request or amount")
    return {"account_no": payload.account_no, "balance": new_balance}


@router.post("/withdraw", response_model=BalanceResponse)
async def withdraw(payload: WithdrawRequest):
    if not auth.login(payload.account_no, payload.password):
        raise HTTPException(status_code=401, detail="Unauthorized: invalid account or password")
    ref = payload.reference or "Cash Withdrawal"
    new_balance = service.withdraw(payload.account_no, payload.password, payload.amount, reference=ref)
    if new_balance is None or new_balance is False:
        raise HTTPException(status_code=400, detail="Insufficient funds or invalid withdrawal amount")
    return {"account_no": payload.account_no, "balance": new_balance}


@router.post("/transfer", response_model=TransferResponse)
async def transfer(payload: TransferRequest):
    if not auth.login(payload.sender_account_no, payload.password):
        raise HTTPException(status_code=401, detail="Unauthorized: invalid sender account or password")
    ref = payload.reference or "Account Transfer"
    result = service.transfer(
        payload.sender_account_no,
        payload.password,
        payload.receiver_account_no,
        payload.amount,
        reference=ref,
    )
    if result is None or result is False:
        raise HTTPException(status_code=400, detail="Transfer failed: check receiver account or balance")
    return {
        "sender_account_no": payload.sender_account_no,
        "receiver_account_no": payload.receiver_account_no,
        "sender_balance": result["sender_balance"],
        "receiver_balance": result["receiver_balance"],
    }
