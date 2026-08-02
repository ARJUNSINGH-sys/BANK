from fastapi import FastAPI
from .routes import auth, customer, transaction

app = FastAPI(
    title="Bank Management API",
    description="REST API for Bank Management System",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(customer.router)
app.include_router(transaction.router)


@app.get("/")
async def read_root():