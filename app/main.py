from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from MAIN.main import initialize_database, seed_sample_data
from database.databade import DATABASE_PATH, db
from .routes import auth, customer, transaction

ROOT_DIR = Path(__file__).resolve().parents[1]


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_path = DATABASE_PATH
    schema_path = str(ROOT_DIR / "database" / "branch.sql")
    try:
        initialize_database(db_path, schema_path)
        seed_sample_data(db)
        print("Database initialized and sample data seeded.")
    except Exception as e:
        print(f"Database initialization warning: {e}")
    yield


app = FastAPI(
    title="Seva Bank Portal API",
    description="RESTful Banking APIs for account management, customer service, and transaction processing.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(customer.router)
app.include_router(transaction.router)

frontend_dir = ROOT_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
