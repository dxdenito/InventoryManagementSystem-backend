from fastapi import APIRouter,Depends , HTTPException
from sqlalchemy.orm import Session
from database import sessionLocal
from schemas import ProductCreate
import models
from routes.auth import get_current_user


router =APIRouter()
def get_db():
    db = sessionLocal()
    try:
        yield db

    finally:
        db.close()



@router.post("/")
def create_product(product: ProductCreate, current_user: models.User = Depends(get_current_user), db: Session=Depends(get_db)):
    new_product = models.Product(product_name=product.product_name, sku=product.sku, price=product.price, shop_id=product.shop_id)
    db.add(new_product)
    db.flush()
    
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/")
def get_products(shop_id: int, status:str="active", current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(models.Product).filter(models.Product.shop_id == shop_id)
    if status == "active":
        query = query.filter(models.Product.is_active == True)
    elif status == "inactive":
        query = query.filter(models.Product.is_active == False)
    elif status == "all":
        pass
    return query.all()

@router.put("/delete_product/{product_id}")
def delete_product( product_id:int, current_user: models.User = Depends(get_current_user),db: Session = Depends(get_db)):
    product= db.query(models.Product).filter(models.Product.id == product_id).first()

    if not product:
        return {"error":"Product not found"}
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this product")
    product.is_active=False
    db.commit()

    return {"message":"Product deleted"}


@router.put("/activate_product/{product_id}")
def activate_product( product_id:int, current_user: models.User = Depends(get_current_user),db: Session = Depends(get_db)):
    product= db.query(models.Product).filter(models.Product.id == product_id).first()

    if not product:
        return {"error":"Product not found"}
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this product")
    product.is_active=True
    db.commit()

    return {"message":"Product activated"}