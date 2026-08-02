from pydantic import BaseModel, EmailStr


class CustomerCreateRequest(BaseModel):
    password: str
    name: str
    personal_id_type: str
    personal_id: str
    address: str
    phone_no: int
    email: EmailStr
    branch_no: int


class CustomerUpdateRequest(BaseModel):
    password: str | None = None
    name: str | None = None
    address: str | None = None
    phone_no: int | None = None
    email: EmailStr | None = None
