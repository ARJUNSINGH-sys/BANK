from fastapi import APIRouter

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("/")
def list_transactions():
    return {"transactions": []}
