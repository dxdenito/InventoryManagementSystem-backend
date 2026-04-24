from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
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

@router.get("/analytics")
def analytics(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    threshold = 5

    # 🔐 OWNER → all shops
    if current_user.role == "owner":

        # total shops
        total_shops = db.query(models.Shop).filter(
            models.Shop.owner_id == current_user.id
        ).count()

        # products across all shops
        products_query = db.query(models.Product).join(models.Shop).filter(
            models.Shop.owner_id == current_user.id
        )

    else:
        total_shops = 1

        products_query = db.query(models.Product).filter(
            models.Product.shop_id == current_user.shop_id
        )

    total_products = products_query.count()

    total_stock = db.query(func.sum(models.Product.quantity)).scalar() or 0

    low_stock = products_query.filter(
        models.Product.quantity <= threshold
    ).count()

    # 🔥 recent activity
    if current_user.role == "owner":
        recent_activity = db.query(models.InventoryMovement)\
            .join(models.Shop)\
            .filter(models.Shop.owner_id == current_user.id)\
            .order_by(models.InventoryMovement.created_at.desc())\
            .limit(5).all()
    else:
        recent_activity = db.query(models.InventoryMovement)\
            .filter(models.InventoryMovement.shop_id == current_user.shop_id)\
            .order_by(models.InventoryMovement.created_at.desc())\
            .limit(5).all()

    # 🔥 stock per shop (chart data)
    stock_by_shop = db.query(
        models.Shop.name,
        func.sum(models.Product.quantity)
    ).join(models.Product)\
     .group_by(models.Shop.name).all()

    return {
        "total_products": total_products,
        "total_shops": total_shops,
        "total_stock": total_stock,
        "low_stock": low_stock,
        "recent_activity": [
            {
                "id": a.id,
                "quantity": a.quantity,
                "type": a.movement_type,
                "date": a.created_at
            } for a in recent_activity
        ],
        "stock_by_shop": [
            {"shop": s[0], "stock": s[1]} for s in stock_by_shop
        ]
    }