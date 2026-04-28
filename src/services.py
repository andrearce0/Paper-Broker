from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import models
import schemas
import crud
import security
from fpdf import FPDF
from datetime import datetime
import aws_s3
import yfinance as yf
import logging

logger = logging.getLogger(__name__)

def validate_sell_operation(db: Session, user_id: int, asset_id: int, quantity_to_sell: float):
    """Regra de negócio: Impede venda a descoberto (short selling sem margem)."""
    transactions = crud.get_transactions_by_user_and_asset(db, user_id, asset_id)
    
    balance = sum(t.quantity if t.type == models.TransactionType.BUY else -t.quantity for t in transactions)
    
    if quantity_to_sell > balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Saldo em custódia insuficiente. Você possui {balance} cotas."
        )

def generate_portfolio_summary(db: Session, current_user: models.User):
    """Regra de negócio: Calcula o preço médio e a posição atual da carteira."""
    transactions = crud.get_transactions_by_user(db, current_user.id, limit=None)
    portfolio = {}

    for t in transactions:
        ticker = t.asset.ticker
        if ticker not in portfolio:
            portfolio[ticker] = {
                "name": t.asset.name, 
                "quantity": 0.0, 
                "total_cost": 0.0,
                "average_price": 0.0
            }
        
        state = portfolio[ticker]

        if t.type == models.TransactionType.BUY:
            state["total_cost"] += (t.quantity * t.price)
            state["quantity"] += t.quantity
            # Atualiza o preço medio
            state["average_price"] = state["total_cost"] / state["quantity"]

        elif t.type == models.TransactionType.SELL:
            cost_of_sold_shares = t.quantity * state["average_price"]
            
            state["quantity"] -= t.quantity
            state["total_cost"] -= cost_of_sold_shares
            
            if state["quantity"] <= 0:
                state["quantity"] = 0
                state["total_cost"] = 0
                state["average_price"] = 0

    assets_list = []
    for ticker, data in portfolio.items():
        if data["quantity"] > 0:
            assets_list.append(schemas.AssetSummary(
                ticker=ticker,
                name=data["name"],
                total_quantity=data["quantity"], 
                average_price=round(data["average_price"], 2),
                total_invested=round(data["total_cost"], 2)
            ))
            
    total_value = sum(asset.total_invested for asset in assets_list)
    
    return {
        "investor_name": current_user.full_name,
        "assets": assets_list,
        "total_portfolio_value": total_value
    }

def generate_portfolio_performance(db: Session, current_user: models.User):
    transactions = crud.get_transactions_by_user(db, user_id=current_user.id, limit=None)
    
    performance_dict = {}
    
    portfolio_state = {}

    for t in transactions:
        asset_id = t.asset_id
        asset_name = t.asset.name 
        
        if asset_id not in portfolio_state:
            portfolio_state[asset_id] = {"quantity": 0, "average_price": 0.0}
            
        if asset_id not in performance_dict:
            performance_dict[asset_id] = {
                "ticker": asset_name,
                "quantity": 0,       
                "average_price": 0.0,
                "realized_profit": 0.0,
                "receipt_url": getattr(t, "receipt_url", None) 
            }

        if t.type == models.TransactionType.BUY:
            curr_qty = portfolio_state[asset_id]["quantity"]
            curr_avg = portfolio_state[asset_id]["average_price"]
            
            total_cost = (curr_qty * curr_avg) + (t.quantity * t.price)
            new_qty = curr_qty + t.quantity
            
            portfolio_state[asset_id]["quantity"] = new_qty
            portfolio_state[asset_id]["average_price"] = total_cost / new_qty

        elif t.type == models.TransactionType.SELL:
            curr_avg = portfolio_state[asset_id]["average_price"]
            
            profit = (t.price - curr_avg) * t.quantity
            
            portfolio_state[asset_id]["quantity"] -= t.quantity
            
            performance_dict[asset_id]["quantity"] += t.quantity  # Soma quantas foram vendidas no total
            performance_dict[asset_id]["realized_profit"] += profit
            performance_dict[asset_id]["average_price"] = curr_avg # Mostra o custo daquela operação

    assets_list = list(performance_dict.values())
    
    assets_performance = [asset for asset in assets_list if asset["quantity"] > 0]
    
    total_profit = sum(asset["realized_profit"] for asset in assets_performance)

    return {
        "investor_name": current_user.full_name,
        "total_realized_profit": total_profit,
        "assets_performance": assets_performance
    }

def create_user(db: Session, user_schema: schemas.UserCreate):
    """Função para registro do usuário"""
    db_user = crud.get_user_by_email(db, email=user_schema.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="E-mail já registrado na base de dados."
        )
    
    new_user = crud.create_user(db, user_schema)
    db.commit()
    db.refresh(new_user)
    
    return new_user

def authenticate_and_generate_token(db: Session, email: str, password: str):
    """Regra de negócio: Valida credenciais e emite o Token JWT."""
    user = crud.get_user_by_email(db, email=email)
    
    if not user or not security.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(data={"sub": user.email, "is_admin": user.is_admin})
    
    return {"access_token": access_token, "token_type": "bearer"}

def create_transaction(db: Session, transaction: schemas.TransactionCreate, current_user: models.User):
    asset = crud.get_asset(db, asset_id=transaction.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Ação não encontrada")
    
    if transaction.type == models.TransactionType.SELL:
        validate_sell_operation(db, user_id=current_user.id, asset_id=transaction.asset_id, quantity_to_sell=transaction.quantity)

    try:
        market_price = fetch_current_market_price(asset.ticker)
        
        tolerance = 0.02 
        diff = abs(transaction.price - market_price) / market_price
        
        if diff > tolerance:
            raise HTTPException(
                status_code=400, 
                detail=f"Preço fora da margem. Mercado: {market_price:.2f}, Enviado: {transaction.price:.2f}"
            )
    except HTTPException:
        raise
    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"Erro crítico na validação de preço para {asset.ticker}. Falha interna: {error_type}")
        
        raise HTTPException(
            status_code=503, 
            detail="Serviço de cotação temporariamente indisponível. Tente novamente."
        )

    new_transaction = crud.create_transaction(db=db, transaction=transaction, user_id=current_user.id)
    db.commit()
    db.refresh(new_transaction)
    
    return process_transaction_receipt(db, new_transaction, asset, current_user)

def create_asset(db: Session, asset: schemas.AssetCreate):
    existing_asset = crud.get_asset_by_ticker(db, ticker=asset.ticker)
    if existing_asset:
        raise HTTPException(
            status_code=400, 
            detail=f"O ativo com ticker '{asset.ticker}' já está cadastrado."
        )

    new_asset = crud.create_asset(db=db, asset=asset)
    
    db.commit()
    db.refresh(new_asset)
    
    return new_asset

def get_user(db: Session, user_id: int):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investidor não encontrado"
        )
    return db_user

def process_transaction_receipt(db: Session, transaction: models.Transaction, asset: models.Asset, user: models.User):
    """
    Coordena a geração, o upload e a persistência do link do recibo.
    """
    try:
        # Chama a funcao que desenha o PDF e retorna os bytes
        pdf_content = generate_transaction_receipt_pdf(
            user_name=user.full_name, 
            transaction=transaction,
            asset_name=asset.name
        )
        
        # Envia os bytes para o S3
        receipt_url = aws_s3.upload_file_to_s3(
            file_bytes=pdf_content,
            original_filename=f"recibo_{transaction.id}.pdf",
            content_type="application/pdf"
        )
        
        # Atualiza a transacao com a URL devolvida pela AWS
        transaction.receipt_url = receipt_url
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
    except Exception as e:
        error_type = type(e).__name__
        
        logger.error(f"Aviso: Falha na geracao/upload do recibo para a transação {transaction.id}. Erro: {error_type}")
    
    return transaction

def generate_transaction_receipt_pdf(user_name: str, transaction: models.Transaction, asset_name: str):
    """Gera um PDF formatado em memória e retorna os bytes."""
    pdf = FPDF()
    pdf.add_page()
    
    # Cabecalho
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "INVESTIMENTO - COMPROVANTE", ln=True, align="C")
    pdf.ln(10)
    
    # Detalhes do Investidor
    pdf.set_font("Arial", size=12)
    pdf.cell(190, 10, f"Investidor: {user_name}", ln=True)
    pdf.cell(190, 10, f"Data da Operação: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True)
    pdf.ln(5)
    
    # Detalhes da Transacao
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(95, 10, "Descrição", border=1, fill=True)
    pdf.cell(95, 10, "Valor", border=1, fill=True, ln=True)
    
    pdf.set_font("Arial", size=12)
    tipo = "COMPRA" if transaction.type == models.TransactionType.BUY else "VENDA"
    
    pdf.cell(95, 10, f"Ativo: {asset_name}", border=1)
    pdf.cell(95, 10, f"{tipo}", border=1, ln=True)
    
    formated_quantity = int(transaction.quantity) if transaction.quantity % 1 == 0 else transaction.quantity

    pdf.cell(95, 10, f"Quantidade: {formated_quantity}", border=1)
    pdf.cell(95, 10, f"Preço Unitário: R$ {transaction.price:.2f}", border=1, ln=True)
    
    pdf.set_font("Arial", "B", 12)
    total = transaction.quantity * transaction.price
    pdf.cell(95, 10, "VALOR TOTAL:", border=1)
    pdf.cell(95, 10, f"R$ {total:.2f}", border=1, ln=True)
    
    pdf.ln(20)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(190, 10, f"ID da Transação: {transaction.id} | Autenticação Digital S3", align="C")
    
    return pdf.output()

def get_assets(db: Session, skip: int = 0, limit: int = 100):
    """
    Regra de negócio para listagem de ativos.
    """
    return crud.get_assets(db, skip=skip, limit=limit)

def get_user_transactions(db: Session, user_id: int):
    """
    Busca as transações do usuário e injeta dados dinâmicos, 
    como o Ticker do ativo e a URL temporária do S3.
    """
    transactions = crud.get_transactions_by_user(db, user_id=user_id)
    
    for t in transactions:
        if t.receipt_url:
            file_key = t.receipt_url.split('/')[-1] 
            t.receipt_url = aws_s3.generate_presigned_url(file_key)
            
    return transactions

def fetch_current_market_price(ticker: str) -> float:
    """Busca o preço atual do ativo."""
    stock = yf.Ticker(ticker)
    todays_data = stock.history(period='1d')
    
    if todays_data.empty:
        raise ValueError(f"Ticker {ticker} não encontrado.")
        
    return float(todays_data['Close'].iloc[-1])