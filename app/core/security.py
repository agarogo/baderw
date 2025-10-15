# app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Any
from jose import jwt, JWTError

# ВАЖНО: этот ключ и алгоритм должны совпадать с теми, что используются в /auth/token
SECRET_KEY = "SD3sf356Dfd09fRt4"   # возьми из .env / настроек
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

def create_access_token(subject: Union[str, int], expires_delta: Optional[timedelta] = None) -> str:
  expire = datetime.now(tz=timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
  payload: dict[str, Any] = {"sub": str(subject), "exp": int(expire.timestamp())}
  return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    sub = payload.get("sub")
    exp = payload.get("exp")
    if sub is None or exp is None:
      raise JWTError("invalid payload")
    # sub может быть email или id (число)
    try:
      sub_val: Union[int, str] = int(sub)
    except Exception:
      sub_val = str(sub)
    return {"sub": sub_val, "exp": int(exp)}
  except JWTError as e:
    raise e
