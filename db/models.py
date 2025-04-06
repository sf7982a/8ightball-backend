// /backend/db/models.py
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"
    id = Column(String, primary_key=True)
    name = Column(String)
    subscription_plan = Column(String, default="free")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    account_id = Column(String, ForeignKey("accounts.id"))
    email = Column(String, unique=True)
    role = Column(String)
    password_hash = Column(String)

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id = Column(String, primary_key=True)
    account_id = Column(String, ForeignKey("accounts.id"))
    rfid_tag = Column(String, unique=True)
    name = Column(String)
    volume_ml = Column(Integer)
    added_by = Column(String, ForeignKey("users.id"))
    added_at = Column(DateTime, default=datetime.datetime.utcnow)

class RFIDScanLog(Base):
    __tablename__ = "rfid_scans"
    id = Column(String, primary_key=True)
    rfid_tag = Column(String)
    scanned_at = Column(DateTime, default=datetime.datetime.utcnow)
    scanned_by = Column(String, ForeignKey("users.id"))