from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy.orm import Session
from database import sessionLocal
from schemas import InventoryCreate
import models
from routes.auth import get_current_user

router =APIRouter()
def get_db():
    db = sessionLocal()
    try:
        yield db

    finally:
        db.close()

@router.get("/")
def get_inventories(db: Session = Depends(get_db)):
    return db.query(models.InventoryMovement).all()

@router.post("/add_inventory")
def add_inventory(inventory : InventoryCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == inventory.product_id).first()
    if not product:
        return HTTPException(status_code=404, detail="Product not found")
    if current_user.role not in ["owner", "admin","store"] : 
        raise HTTPException(status_code=403, detail="Not authorized to add inventory for this product")
    product.quantity += inventory.quantity
    new_inventory= models.InventoryMovement(product_id=product.id,quantity = inventory.quantity, movement_type="IN", user_id=current_user.id, shop_id=product.shop_id)
    db.add(new_inventory)
    db.flush()
    db.commit()
    db.refresh(new_inventory)
    return {"mesage":"Stock added"}

@router.post("/remove_inventory")
def remove_inventory(inventory : InventoryCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == inventory.product_id).first()
    if not product:
        return HTTPException(status_code=404, detail="Product not found")
    if current_user.role not in ["owner", "admin","store"] :
        raise HTTPException(status_code=403, detail="Not authorized to add inventory for this product")
    if product.quantity < inventory.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock available")
    product.quantity -= inventory.quantity

    new_inventory= models.InventoryMovement(product_id=product.id,quantity = inventory.quantity, movement_type="OUT", user_id=current_user.id, shop_id=product.shop_id)
    db.add(new_inventory)
    db.flush()
    db.commit()
    db.refresh(new_inventory)
    return {"message": "Stock removed"}

@router.get("/history/{product_id}")
def get_history(product_id: int, db: Session = Depends(get_db)):
    return db.query(models.InventoryMovement).filter(models.InventoryMovement.product_id == product_id).order_by(models.InventoryMovement.created_at.desc()).all()