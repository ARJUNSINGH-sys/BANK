from fastapi import APIRouter, HTTPException
from ..schemas.customer import CustomerCreateRequest, CustomerUpdateRequest
from ..services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"])
service = CustomerService()


@router.post("/")
async def create_customer(payload: CustomerCreateRequest):
    customer_id = service.create_customer(payload)
    if customer_id is None:
        raise HTTPException(status_code=400, detail="Could not create customer")
    return {"customer_id": customer_id}


@router.put("/{customer_id}")
async def update_customer(customer_id: int, payload: CustomerUpdateRequest):
    if not service.update_customer(customer_id, payload):
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer updated"}


@router.delete("/{customer_id}")
async def delete_customer(customer_id: int):
    if not service.delete_customer(customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted"}
