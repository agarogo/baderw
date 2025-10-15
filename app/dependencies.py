# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, ExpiredSignatureError

from app.core.security import decode_token
from app.db import get_db               # твоя функция выдаёт Session
from app.models import User             # твоя модель пользователя

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)

credentials_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise credentials_exc
    try:
        data = decode_token(token)  # sub: str|int (email или id)
        user: User | None = None

        # sub=int? значит это id
        if isinstance(data.sub, int):
            user = db.query(User).get(data.sub)
        else:
            sub_str = str(data.sub)
            if "@" in sub_str:
                user = db.query(User).filter(User.email_user == sub_str).first()
            else:
                # на всякий случай — если вдруг решили класть nickname
                user = db.query(User).filter(User.nickname == sub_str).first()

        if not user:
            raise credentials_exc
        return user

    except ExpiredSignatureError:
        raise credentials_exc
    except JWTError:
        raise credentials_exc
