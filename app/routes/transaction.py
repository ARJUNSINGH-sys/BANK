from fastapi import APIRouter, HTTPException
from ..schemas.transaction import (
    BalanceRequest,
    BalanceResponse,
    DepositRequest,
    TransferRequest,
    TransferResponse,
    WithdrawRequest,
)
from ..services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["transactions"])
service = TransactionService()


@router.post("/balance", response_model=BalanceResponse)
async def get_balance(payload: BalanceRequest):
    current_balance = service.get_balance(payload.account_no, payload.password)
    if current_balance is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"account_no": payload.account_no, "balance": current_balance}


@router.post("/deposit", response_model=BalanceResponse)
async def deposit(payload: DepositRequest):
    new_balance = service.deposit(payload.account_no, payload.password, payload.amount)
    if new_balance is None:
        raise HTTPException(status_code=400, detail="Invalid credentials or amount")
    return {"account_no": payload.account_no, "balance": new_balance}


@router.post("/withdraw", response_model=BalanceResponse)
async def withdraw(payload: WithdrawRequest):
    new_balance = service.withdraw(payload.account_no, payload.password, payload.amount)
    if new_balance is None:
        raise HTTPException(status_code=400, detail="Invalid credentials or insufficient funds")
    return {"account_no": payload.account_no, "balance": new_balance}


@router.post("/transfer", response_model=TransferResponse)
async def transfer(payload: TransferRequest):
    result = service.transfer(
        payload.sender_account_no,
        payload.password,
        payload.receiver_account_no,
        payload.amount,
    )
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid credentials or insufficient funds")
    return {
        "sender_account_no": payload.sender_account_no,
        "receiver_account_no": payload.receiver_account_no,
        "sender_balance": result["sender_balance"],
        "receiver_balance": result["receiver_balance"],
    }

