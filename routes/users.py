from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from database import sessionLocal
from schemas import UserCreate
import models

router =APIRouter()
def get_db():
    db = sessionLocal()
    try:
        yield db

    finally:
        db.close()

@router.get("/")
def root():
    return {"message":"users route"}

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()