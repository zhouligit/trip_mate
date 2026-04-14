from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models import Group, Rating, User

router = APIRouter()


class RatingRequest(BaseModel):
    group_id: int
    mate_score: int = Field(ge=1, le=5)
    route_score: int = Field(ge=1, le=5)
    bus_score: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=500)


@router.post("")
def submit_rating(
    payload: RatingRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    group = db.get(Group, payload.group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    rating = db.scalar(select(Rating).where(Rating.group_id == payload.group_id, Rating.user_id == user.id))
    if not rating:
        rating = Rating(
            group_id=payload.group_id,
            user_id=user.id,
            mate_score=payload.mate_score,
            route_score=payload.route_score,
            bus_score=payload.bus_score,
            comment=payload.comment,
        )
        db.add(rating)
    else:
        rating.mate_score = payload.mate_score
        rating.route_score = payload.route_score
        rating.bus_score = payload.bus_score
        rating.comment = payload.comment
    db.commit()
    return {"rating_id": rating.id, "group_id": payload.group_id}
