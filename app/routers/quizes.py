# app/routers/quizes.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies import get_current_user
from app.db import get_db
from app.models import User

router = APIRouter()

class GameResultIn(BaseModel):
    score: int
    duration_sec: int

def compute_award(score: int, duration_sec: int) -> int:
    # базовая формула: 2 монеты за очко, + бонус за скорость
    base = max(0, score) * 2
    speed = 0
    if duration_sec > 0:
        speed = min(base // 2, max(0, (score * 10) // max(1, duration_sec // 10)))
    return max(0, base + speed)

@router.post("/quizes/games/result")
def post_game_result(
    payload: GameResultIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    awarded = compute_award(payload.score, payload.duration_sec)
    user.coins = (user.coins or 0) + awarded
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"ok": True, "awarded": awarded, "coins": user.coins}
