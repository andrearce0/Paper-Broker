from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime
from database import Base

Base = declarative_base()

class TransactionType(enum.Enum):
    BUY = "compra"
    SELL = "venda"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    
    transactions = relationship("Transaction", back_populates="owner")

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True, nullable=False) # Ex: PETR4, IVVB11
    name = Column(String, nullable=False)
    asset_type = Column(String)

    transactions = relationship("Transaction", back_populates="asset")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    asset_id = Column(Integer, ForeignKey("assets.id"))
    
    type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False) # Preço unitário na data
    timestamp = Column(DateTime, default=datetime.utcnow)
    receipt_url = Column(String, nullable=True)

    owner = relationship("User", back_populates="transactions")
    asset = relationship("Asset", back_populates="transactions")

    @property
    def ticker(self):
        return self.asset.ticker if self.asset else "N/A"