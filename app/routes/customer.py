from fastapi import APIRouter, HTTPException
from ..schemas.customer import (
    CustomerCreateRequest,
    CustomerUpdateRequest,
    CustomerDeleteRequest,
    CustomerResponse,
)
from ..services.customer_service import CustomerService
from ..services.auth_service import AuthService

router = APIRouter(prefix="/customers", tags=["customers"])
service = CustomerService()
auth = AuthService()


@router.get("/", response_model=list[CustomerResponse])
async def list_customers():
    return service.list_customers()


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int):
    customer = service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("/", response_model=dict)
async def create_customer(payload: CustomerCreateRequest):
    customer_id = service.create_customer(payload)
    if customer_id is None:
        raise HTTPException(status_code=400, detail="Could not create customer")
    return {"customer_id": customer_id, "message": "Customer account created successfully"}


@router.put("/{customer_id}")
async def update_customer(customer_id: int, payload: CustomerUpdateRequest):
    if not service.update_customer(customer_id, payload):
        raise HTTPException(status_code=404, detail="Customer not found or no changes made")
    return {"message": "Customer updated"}


@router.delete("/{customer_id}")
async def delete_customer(customer_id: int, payload: CustomerDeleteRequest):
    if not auth.login(payload.account_no, payload.password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not service.delete_customer(customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}
