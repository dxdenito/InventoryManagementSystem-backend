from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from database import sessionLocal
from models import User, Shop
from schemas import UserLogin, UserCreate
from utils import hash_password, verify_password, create_access_token

router = APIRouter()
security = HTTPBearer(auto_error=False)

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"


# ✅ DB DEPENDENCY
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()



def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: int = payload.get("user_id")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user



@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        username=user.username,
        role="owner",
        email=user.email,
        must_change_password=False,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    
    shop = Shop(
        name=user.shopName,
        owner_id=new_user.id,
        description=user.description,
        location=user.location
    )

    db.add(shop)
    db.commit()
    db.refresh(shop)

    # 🔥 assign shop to user
    new_user.shop_id = shop.id
    db.commit()

    return {"message": "user created"}



@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "user_id": db_user.id,
        "shop_id": db_user.shop_id,
        "role": db_user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "must_change_password": db_user.must_change_password
    }


# ✅ CHANGE PASSWORD (FIXED BODY INPUT)
from pydantic import BaseModel

class ChangePasswordSchema(BaseModel):
    new_password: str


@router.post("/change-password")
def change_password(
    data: ChangePasswordSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hash_password(data.new_password)
    user.must_change_password = False

    db.commit()

    return {"message": "Password changed successfully"}



@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user