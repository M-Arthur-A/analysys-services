from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt

from app.users.repo import UsersDAO
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=1)
    expire = expire.replace(hour=5, minute=0)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORYTM)
    return encoded_jwt

async def authenticate_user(username: str, password: str):
    user = await UsersDAO.find_one_or_none(username=username)
    if user and verify_password(password, user.hashed_password):
        return user
