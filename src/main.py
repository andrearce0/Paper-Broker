from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import engine
import services
from dependencies import get_db, get_current_user, get_current_admin
import logging
models.Base.metadata.create_all(bind=engine)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Gestao de Investimentos API",
    description="API para gestão de carteiras de investimento e transações.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "app-paperbroker.netlify.app"], # Permite o seu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "API de Investimentos operando com sucesso."}

@app.post("/users/", response_model=schemas.UserResponse, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return services.create_user(db=db, user_schema=user)

@app.post("/login", response_model=schemas.Token, tags=["Auth"])
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    # O form_data do OAuth2 mapeia o e-mail para o campo 'username'
    return services.authenticate_and_generate_token(
        db=db, 
        email=form_data.username, 
        password=form_data.password
    )

@app.get("/users/{user_id}", response_model=schemas.UserResponse, tags=["Users"])
def read_user(user_id: int, 
              db: Session = Depends(get_db),
              user: models.User = Depends(get_current_admin)):
    return services.get_user(db, user_id)

# --- ROTAS DE ATIVOS ---

@app.post("/assets/", response_model=schemas.AssetResponse, tags=["Assets"])
def create_asset(
    asset: schemas.AssetCreate, 
    db: Session = Depends(get_db),
    # Ao colocar esta dependência, o FastAPI extrai o token, 
    # roda a nossa função lá de cima e barra se não for admin!
    admin_data: dict = Depends(get_current_admin) 
):
    return services.create_asset(db=db, asset=asset)

@app.get("/assets/", response_model=List[schemas.AssetResponse], tags=["Assets"])
def read_assets(skip: int = 0, 
                limit: int = 100, 
                db: Session = Depends(get_db), 
                user: models.User = Depends(get_current_user)):
    return services.get_assets(db=db, skip=skip, limit=limit)

# --- ROTAS DE TRANSAÇÕES ---

@app.post("/transactions/", response_model=schemas.TransactionResponse, tags=["Transactions"])
def create_transaction(transaction: schemas.TransactionCreate, 
                       db: Session = Depends(get_db),
                       current_user: models.User = Depends(get_current_user)):
    return services.create_transaction(db, transaction, current_user)

@app.get("/portfolio/summary", response_model=schemas.PortfolioSummary, tags=["Portfolio"])
def read_portfolio_summary(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """Retorna o resumo consolidado de todos os ativos na carteira do investidor logado."""
    return services.generate_portfolio_summary(db=db, current_user=current_user)

@app.get("/portfolio/performance", response_model=schemas.PortfolioPerformance, tags=["Portfolio"])
def read_portfolio_performance(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """Retorna o relatório de Lucro/Prejuízo realizado pelo investidor."""
    return services.generate_portfolio_performance(db=db, current_user=current_user)

@app.get("/transactions/me", response_model=List[schemas.TransactionResponse])
def read_user_transactions(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    return services.get_user_transactions(db=db, user_id=current_user.id)

from fastapi import HTTPException
import services # certifique-se de importar o módulo

@app.get("/assets/{ticker}/price", tags=["Assets"])
def get_realtime_price(ticker: str, user: models.User = Depends(get_current_user)):
    try:
        # Repassa a responsabilidade para a camada de serviço
        price = services.fetch_current_market_price(ticker)
        
        return {"ticker": ticker, "price": round(price, 2)}
        
    except Exception as e:
        # Pega apenas o nome da classe do erro (ex: 'TimeoutError', 'ValueError')
        # Isso impede que URLs, tokens ou caminhos do sistema vazem no console
        error_type = type(e).__name__
        
        # Loga de forma segura e padronizada
        logger.error(f"Falha na integracao de cotacao para {ticker}. Erro interno: {error_type}")
        
        # O usuário final continua vendo apenas a mensagem amigável e segura
        raise HTTPException(status_code=400, detail="Cotação indisponível no momento")