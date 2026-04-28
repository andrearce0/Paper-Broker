from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import List, Optional
from models import TransactionType

class AssetBase(BaseModel):
    ticker: str = Field(..., example="PETR4", description="Código de negociação do ativo")
    name: str = Field(..., example="Petrobras PN")
    asset_type: str = Field(..., example="Ação")

class AssetCreate(AssetBase):
    pass

class AssetResponse(AssetBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True) 

class AssetPerformance(BaseModel):
    ticker: str
    quantity: float
    average_price: float
    realized_profit: float
    receipt_url: Optional[str] = None

class AssetSummary(BaseModel):
    ticker: str
    name: str
    total_quantity: float
    average_price: float
    total_invested: float

class TransactionBase(BaseModel):
    type: TransactionType
    quantity: float = Field(..., gt=0, description="Quantidade negociada")
    price: float = Field(..., gt=0, description="Preço unitário do ativo na negociação")

class TransactionCreate(TransactionBase):
    asset_id: int

class TransactionResponse(BaseModel):
    id: int
    type: str # 'BUY' ou 'SELL'
    quantity: float
    price: float
    asset_id: int
    ticker: str
    timestamp: datetime
    receipt_url: Optional[str] = None # O campo chave para o link do S3

    class Config:
        from_attributes = True

class TransactionReceiptResponse(BaseModel):
    transaction: TransactionResponse
    receipt_url: Optional[str] = None

class UserBase(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr 

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: int
    transactions: List[TransactionResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class PortfolioSummary(BaseModel):
    investor_name: str
    assets: List[AssetSummary]
    total_portfolio_value: float
    
    model_config = ConfigDict(from_attributes=True)

class PortfolioPerformance(BaseModel):
    investor_name: str
    total_realized_profit: float
    assets_performance: List[AssetPerformance]
