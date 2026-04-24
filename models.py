from database import Base

from sqlalchemy import Column, Integer, String, TIMESTAMP,ForeignKey, Boolean, text
from sqlalchemy.orm import relationship


class Product(Base):
    __tablename__="products"

    id= Column(Integer, primary_key=True, nullable=False)
    product_name = Column(String)
    sku =Column(String, unique=True)
    price = Column(Integer)
    quantity = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    is_active = Column(Boolean, default=True)
    shop_id = Column(Integer, ForeignKey("shops.id"))

    inventory = relationship(
        "InventoryMovement",
        backref="product",
        cascade="all, delete"
    )


class InventoryMovement(Base):
    __tablename__ ="inventory_movements"

    id= Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    movement_type= Column(String) 
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    user_id = Column(Integer, ForeignKey("users.id"))
    shop_id = Column(Integer, ForeignKey("shops.id"))

class User(Base):
    __tablename__="users"

    id= Column(Integer,primary_key=True, index=True)
    username=Column(String, nullable=False)
    email=Column(String, nullable=False)
    password = Column(String, nullable=False)
    must_change_password = Column(Boolean, default=True)
    role = Column(String, default="user")
    shop_id = Column(Integer, ForeignKey("shops.id"))
    is_active = Column(Boolean, default=True)
    owned_shops = relationship("Shop", back_populates="owner", foreign_keys="Shop.owner_id")
    shop = relationship("Shop", back_populates="employees", foreign_keys=[shop_id])


class Shop(Base):
    __tablename__="shops"

    id= Column(Integer,primary_key=True, index=True)
    name=Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String)
    location =Column(String)
    status = Column(Boolean, default=True)
    owner = relationship("User", back_populates="owned_shops", foreign_keys=[owner_id])
    employees = relationship("User", back_populates="shop", foreign_keys="User.shop_id")