from pydantic import BaseModel, EmailStr


class CustomerCreateRequest(BaseModel):
    password: str
    name: str
    personal_id_type: str
    personal_id: str
    address: str
    phone_no: str
    email: EmailStr
    branch_no: int = 1


class CustomerUpdateRequest(BaseModel):
    password: str | None = None
    name: str | None = None
    personal_id_type: str | None = None
    personal_id: str | None = None
    address: str | None = None
    phone_no: str | None = None
    email: EmailStr | None = None
    branch_no: int | None = None


class CustomerDeleteRequest(BaseModel):
    account_no: int
    password: str


class CustomerResponse(BaseModel):
    account_no: int
    name: str
    personal_id_type: str
    personal_id: str
    address: str
    phone_no: str | int | None = None
    email: EmailStr | None = None
    branch_no: int | None = 1
    branch_name: str | None = "Main Branch"
    balance: float = 0.0