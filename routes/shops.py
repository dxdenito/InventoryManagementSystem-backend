from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy.orm import Session
from database import sessionLocal
from schemas import ShopCreate
import models
from .auth import get_current_user
router =APIRouter()
def get_db():
    db = sessionLocal()
    try:
        yield db

    finally:
        db.close()

@router.get("/")
def root( status: str = "active",current_user: models.User = Depends(get_current_user), db: Session=Depends(get_db)):
    query = db.query(models.Shop).filter(models.Shop.owner_id == current_user.id)
    if status == "active":
        query = query.filter(models.Shop.status == True)
    elif status == "inactive":
        query = query.filter(models.Shop.status == False)
    return query.all()
@router.get("/owner_shops")
def get_owner_shops(current_user: models.User = Depends(get_current_user), db: Session=Depends(get_db)):
    shop = db.query(models.Shop).filter(models.Shop.id == current_user.shop_id).first()
    shops = db.query(models.Shop).filter(models.Shop.owner_id == shop.owner_id).all()
    return shop
@router.post("/create_shop")
def create_shop(shop: ShopCreate, current_user: models.User = Depends(get_current_user), db: Session=Depends(get_db)):
    new_shop = models.Shop(name=shop.name, owner_id=current_user.id,description=shop.description, location=shop.location)
    db.add(new_shop)
    db.flush()
    db.commit()
    db.refresh(new_shop)
    return new_shop

@router.put("/delete/{shop_id}")
def delete_shop(shop_id: int,  current_user: models.User = Depends(get_current_user), db: Session=Depends(get_db)):
    shop = db.query(models.Shop).filter(models.Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    if shop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this shop")
    shop.status = False
    db.commit()
    return {"message": "Shop deactivated"}
@router.put("/activate_shop/{shop_id}")
def activate_shop(shop_id: int,  current_user: models.User = Depends(get_current_user), db: Session=Depends(get_db)):
    shop = db.query(models.Shop).filter(models.Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    if shop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this shop")
    shop.status = True
    db.commit()
    return {"message": "Shop activated"}