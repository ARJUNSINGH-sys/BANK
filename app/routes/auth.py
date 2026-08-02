from fastapi import APIRouter, HTTPException
from ..schemas.auth import LoginRequest
from ..services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
service = AuthService()


@router.post("/login")
async def login(payload: LoginRequest):
    success = service.login(payload.account_no, payload.password)
    if not success:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}
