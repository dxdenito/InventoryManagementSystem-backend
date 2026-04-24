import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
origins=[
    "http://localhost:5173","http://127.0.0.1:5173","null",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"]
)
from pydantic import BaseModel
from routes import products, inventory,users, shops, auth,employees,dashboard,reports

from database import engine, Base




class Product(BaseModel):
    product_name: str
    sku: str
    price:int

class Inventory(BaseModel):
    product_id:int
    quantity: int
Base.metadata.create_all(bind=engine)
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(inventory.router, prefix="/inventory", tags=["Inventories"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(shops.router, prefix="/shops", tags=["Shops"])
app.include_router(auth.router, prefix="/auth", tags=["Auths"])
app.include_router(employees.router, prefix="/employees", tags=["Employees"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])

@app.get("/")
def home():
    return {"message": "Inventory API running"}

