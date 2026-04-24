from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from database import sessionLocal
from routes.auth import get_current_user
import models

router = APIRouter()


# 🔌 DB DEPENDENCY
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🧠 HELPER → ROLE FILTER
def apply_role_filter(query, current_user):
    if current_user.role == "owner":
        return query.filter(models.Shop.owner_id == current_user.id)
    else:
        return query.filter(models.Product.shop_id == current_user.shop_id)


# 📊 1. STOCK REPORT
@router.get("/stock")
def stock_report(
    shop_id: Optional[int] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Product, models.Shop).join(models.Shop)

    query = apply_role_filter(query, current_user)

    if shop_id:
        query = query.filter(models.Product.shop_id == shop_id)

    results = query.all()

    return [
        {
            "id": p.Product.id,
            "product": p.Product.product_name,
            "quantity": p.Product.quantity,
            "shop": p.Shop.name,
            "is_active": p.Product.is_active
        }
        for p in results
    ]


# 📉 2. LOW STOCK REPORT
@router.get("/low-stock")
def low_stock_report(
    threshold: int = 5,
    shop_id: Optional[int] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Product, models.Shop).join(models.Shop)

    query = apply_role_filter(query, current_user)

    if shop_id:
        query = query.filter(models.Product.shop_id == shop_id)

    results = query.filter(
        models.Product.quantity <= threshold,
        models.Product.is_active == True
    ).all()

    return [
        {
            "id": p.Product.id,
            "product": p.Product.product_name,
            "quantity": p.Product.quantity,
            "shop": p.Shop.name
        }
        for p in results
    ]


# 🔁 3. INVENTORY MOVEMENT REPORT
@router.get("/movements")
def movement_report(
    shop_id: Optional[int] = None,
    limit: int = 20,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(
        models.InventoryMovement,
        models.Product,
        models.Shop,
        models.User
    )\
    .join(models.Product)\
    .join(models.Shop)\
    .join(models.User)

    # 🔐 ROLE FILTER
    if current_user.role == "owner":
        query = query.filter(models.Shop.owner_id == current_user.id)
    else:
        query = query.filter(
            models.InventoryMovement.shop_id == current_user.shop_id
        )

    if shop_id:
        query = query.filter(models.InventoryMovement.shop_id == shop_id)

    results = query.order_by(
        models.InventoryMovement.created_at.desc()
    ).limit(limit).all()

    return [
        {
            "id": r.InventoryMovement.id,
            "product": r.Product.product_name,
            "quantity": r.InventoryMovement.quantity,
            "type": r.InventoryMovement.movement_type,
            "user": r.User.username,
            "shop": r.Shop.name,
            "date": r.InventoryMovement.created_at
        }
        for r in results
    ]


# 📊 4. SUMMARY REPORT (FOR DASHBOARD/REPORTS CARDS)
@router.get("/summary")
def summary_report(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    threshold = 5

    if current_user.role == "owner":
        product_query = db.query(models.Product).join(models.Shop).filter(
            models.Shop.owner_id == current_user.id
        )
        total_shops = db.query(models.Shop).filter(
            models.Shop.owner_id == current_user.id
        ).count()
    else:
        product_query = db.query(models.Product).filter(
            models.Product.shop_id == current_user.shop_id
        )
        total_shops = 1

    total_products = product_query.count()

    total_stock = db.query(func.sum(models.Product.quantity)).scalar() or 0

    low_stock = product_query.filter(
        models.Product.quantity <= threshold
    ).count()

    return {
        "total_products": total_products,
        "total_stock": total_stock,
        "low_stock": low_stock,
        "total_shops": total_shops
    }