from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models import Friendship, User, UserProfile
from app.schemas.friends import AddFriendRequest

router = APIRouter()


@router.post("/add")
def add_friend(
    payload: AddFriendRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    if payload.target_user_id == user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot add yourself")

    target = db.get(User, payload.target_user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = db.scalar(
        select(Friendship).where(
            Friendship.user_id == user.id,
            Friendship.friend_user_id == payload.target_user_id,
        )
    )
    if existing:
        return {"friend_user_id": payload.target_user_id, "already_friend": True}

    db.add(Friendship(user_id=user.id, friend_user_id=payload.target_user_id))
    db.commit()
    return {"friend_user_id": payload.target_user_id, "already_friend": False}


@router.get("")
def list_friends(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    rows = db.scalars(
        select(Friendship).where(Friendship.user_id == user.id).order_by(Friendship.id.desc())
    ).all()
    items = []
    for row in rows:
        fu = db.get(User, row.friend_user_id)
        if not fu:
            continue
        profile = db.scalar(select(UserProfile).where(UserProfile.user_id == fu.id))
        tags = (profile.tags_json or {}).get("tags", []) if profile else []
        items.append(
            {
                "user_id": fu.id,
                "nickname": fu.nickname,
                "avatar_url": fu.avatar_url,
                "city_code": profile.city_code if profile else None,
                "tags": tags,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
        )
    return {"items": items}


@router.delete("/{friend_user_id}")
def remove_friend(
    friend_user_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    row = db.scalar(
        select(Friendship).where(
            Friendship.user_id == user.id,
            Friendship.friend_user_id == friend_user_id,
        )
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friendship not found")
    db.delete(row)
    db.commit()
    return {"friend_user_id": friend_user_id, "removed": True}
