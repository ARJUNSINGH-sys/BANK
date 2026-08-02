from pydantic import BaseModel


class LoginRequest(BaseModel):
    account_no: int
    password: str
