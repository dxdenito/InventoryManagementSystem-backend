from pydantic import BaseModel,EmailStr;

class ProductCreate(BaseModel):
    product_name: str
    sku: str
    price:int
    shop_id: int
    
class InventoryCreate(BaseModel):
    product_id:int
    quantity:int

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    shopName: str
    location: str
    description: str

class UserLogin(BaseModel):
    email:EmailStr
    password: str
class EmployeeCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    shop_id: int
    role: str
class Token(BaseModel):
    access_token:str
    token_type:str

class ShopCreate(BaseModel):
    name:str
    location: str
    description: str


    