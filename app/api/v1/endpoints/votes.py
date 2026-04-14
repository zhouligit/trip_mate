from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models import User, Vote, VoteOption, VoteRecord
from app.schemas.votes import CastVoteRequest

router = APIRouter()


@router.post("/{vote_id}/cast")
def cast_vote(
    vote_id: int,
    payload: CastVoteRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    vote = db.get(Vote, vote_id)
    if not vote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote not found")
    if vote.status != "open":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vote is closed")

    option = db.scalar(select(VoteOption).where(VoteOption.id == payload.option_id, VoteOption.vote_id == vote_id))
    if not option:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid option")

    record = db.scalar(select(VoteRecord).where(VoteRecord.vote_id == vote_id, VoteRecord.user_id == user.id))
    if record:
        return {"vote_id": vote_id, "option_id": record.option_id}

    db.add(VoteRecord(vote_id=vote_id, option_id=payload.option_id, user_id=user.id))
    db.commit()
    return {"vote_id": vote_id, "option_id": payload.option_id}


@router.get("/{vote_id}/result")
def vote_result(vote_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    _ = user
    vote = db.get(Vote, vote_id)
    if not vote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote not found")

    rows = db.execute(
        select(VoteRecord.option_id, func.count(VoteRecord.id))
        .where(VoteRecord.vote_id == vote_id)
        .group_by(VoteRecord.option_id)
        .order_by(func.count(VoteRecord.id).desc())
    ).all()
    stats = [{"option_id": row[0], "count": row[1]} for row in rows]
    winner_option_id = stats[0]["option_id"] if stats else None
    return {"vote_id": vote_id, "winner_option_id": winner_option_id, "stats": stats}
