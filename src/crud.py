from sqlalchemy.orm import Session, joinedload
from typing import Optional
import models
import schemas
import security

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.flush()
    
    return db_user

def get_asset_by_ticker(db: Session, ticker: str):
    return db.query(models.Asset).filter(models.Asset.ticker == ticker).first()

def create_asset(db: Session, asset: schemas.AssetCreate):
    db_asset = models.Asset(
        ticker=asset.ticker,
        name=asset.name,
        asset_type=asset.asset_type
    )
    db.add(db_asset)
    db.flush()
    return db_asset

def get_assets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Asset).offset(skip).limit(limit).all()

def get_asset(db: Session, asset_id: int):
    return db.query(models.Asset).filter(models.Asset.id == asset_id).first()

def create_transaction(db: Session, transaction: schemas.TransactionCreate, user_id: int):
    db_transaction = models.Transaction(
        user_id=user_id,
        asset_id=transaction.asset_id,
        type=transaction.type,
        quantity=transaction.quantity,
        price=transaction.price,
    )
    db.add(db_transaction)
    db.flush()
    
    return db_transaction

def get_transactions_by_user(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: Optional[int] = 100
):
    """
    Busca as transações do usuário. 
    Se limit for None, retorna o histórico completo (útil para relatórios).
    """
    query = db.query(models.Transaction)\
        .options(joinedload(models.Transaction.asset))\
        .filter(models.Transaction.user_id == user_id)\
        .order_by(models.Transaction.timestamp.asc())

    if limit is not None:
        query = query.offset(skip).limit(limit)

    return query.all()

def get_transactions_by_user_and_asset(db: Session, user_id: int, asset_id: int):
    """Busca puramente no banco todas as movimentações de um ativo específico do usuário."""
    return db.query(models.Transaction)\
        .filter(
            models.Transaction.user_id == user_id,
            models.Transaction.asset_id == asset_id
        )\
        .order_by(models.Transaction.timestamp.asc())\
        .all()