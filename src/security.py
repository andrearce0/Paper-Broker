import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from config import settings

def get_password_hash(password: str) -> str:
    """Gera o hash da senha informada."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()

    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto plano bate com o hash salvo no banco."""
    password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password=password_bytes, hashed_password=hashed_password_bytes)

def create_access_token(data: dict):
    """Gera um token JWT válido por um tempo determinado."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt