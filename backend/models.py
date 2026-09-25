from sqlalchemy import Column, Integer, String, Date, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.sql import func


class Receipt(Base):
    __tablename__ = "receipts"
    id = Column(Integer, primary_key=True)
    store_name = Column(String(255))
    purchase_date = Column(Date)
    total_amount = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=func.now())

    items = relationship("ReceiptItem", back_populates="receipt")


class ReceiptItem(Base):
    __tablename__ = "receipt_items"
    id = Column(Integer, primary_key=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"))
    item_name = Column(String(255))
    item_price = Column(Numeric(10, 2))

    receipt = relationship("Receipt", back_populates="items")