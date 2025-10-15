# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.core.security import decode_token
from app.db import get_db           # твоя функция выдаёт Session
from app.models import User         # твоя ORM-модель

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)
cred_exc = HTTPException(
  status_code=status.HTTP_401_UNAUTHORIZED,
  detail="Could not validate credentials",
  headers={"WWW-Authenticate": "Bearer"},
)

def get_current_user(token: str | None = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)) -> User:
  if not token:
    raise cred_exc
  try:
    data = decode_token(token)      # {"sub": str|int, "exp": int}
    sub = data["sub"]
    user: User | None = None

    if isinstance(sub, int):
      user = db.query(User).get(sub)  # id
    else:
      if "@" in sub:
        user = db.query(User).filter(User.email_user == sub).first()  # email
      else:
        user = db.query(User).filter(User.nickname == sub).first()    # запасной вариант

    if not user:
      raise cred_exc
    return user
  except JWTError:
    raise cred_exc
