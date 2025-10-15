# app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

from jose import jwt, JWTError, ExpiredSignatureError

from pydantic import BaseModel

# возьми из .env / настроек
SECRET_KEY = "SD3sf356Dfd09fRt4"             # обязательно совпадает с тем, что используется в /auth/token
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

class TokenData(BaseModel):
    sub: Union[str, int]
    exp: int

def create_access_token(subject: Union[str, int], expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(tz=timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode: dict[str, Any] = {"sub": str(subject), "exp": int(expire.timestamp())}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> TokenData:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    sub = payload.get("sub")
    exp = payload.get("exp")
    if sub is None or exp is None:
        raise JWTError("invalid token payload")
    # sub может быть email или id
    try:
        # пробуем привести к int — если получится, значит id
        sub_cast: Union[int, str] = int(sub)
    except Exception:
        sub_cast = str(sub)
    return TokenData(sub=sub_cast, exp=int(exp))
