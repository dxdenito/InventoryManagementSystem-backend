from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from database import sessionLocal
from schemas import EmployeeCreate
import models
from routes.auth import get_current_user
from utils import hash_password

router =APIRouter()
def get_db():
    db = sessionLocal()
    try:
        yield db

    finally:
        db.close()

@router.post("/create-employee")
def create_employee(employee: EmployeeCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Only shop owners can create employees")
    new_employee = models.User(username=employee.username, email=employee.email,password=hash_password(employee.password), role="employee", shop_id=employee.shop_id)
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

@router.get("/")
def get_employees(status:str="active",current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    owner_shops = db.query(models.Shop).filter(models.Shop.owner_id == current_user.id).all()
    shop_ids = [shop.id for shop in owner_shops]
    query = db.query(models.User).filter(models.User.shop_id.in_(shop_ids))
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Only shop owners can view employees")
    if status == "active":
        query = query.filter(models.User.is_active == True,models.User.role != "owner")
    elif status == "inactive":
        query = query.filter(models.User.is_active == False,models.User.role != "owner")
    return query.all()
   
    return query

@router.put("/deactivate/{employee_id}")
def deactivate_employee(employee_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Only shop owners can deactivate employees")
    employee = db.query(models.User).filter(models.User.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    employee.is_active = False
    db.commit()
    return {"message": "Employee deactivated successfully"}

@router.put("/activate/{employee_id}")
def activate_employee(employee_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Only shop owners can activate employees")
    employee = db.query(models.User).filter(models.User.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    employee.is_active = True
    db.commit()
    return {"message": "Employee activated successfully"}
