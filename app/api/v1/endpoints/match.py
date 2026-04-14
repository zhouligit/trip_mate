from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models import User, UserProfile

router = APIRouter()


@router.get("/recommendations")
def get_recommendations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    me_profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    me_city = me_profile.city_code if me_profile else None
    me_tags = set((me_profile.tags_json or {}).get("tags", [])) if me_profile else set()

    rows = db.execute(
        select(User, UserProfile)
        .join(UserProfile, UserProfile.user_id == User.id)
        .where(User.id != user.id)
        .limit(50)
    ).all()

    candidates = []
    for u, p in rows:
        tags = set((p.tags_json or {}).get("tags", []))
        overlap = len(me_tags.intersection(tags))
        score = min(100, 60 + overlap * 10 + (10 if me_city and p.city_code == me_city else 0))
        candidates.append(
            {
                "user_id": u.id,
                "nickname": u.nickname,
                "avatar_url": u.avatar_url,
                "city_code": p.city_code,
                "tags": list(tags),
                "match_score": score,
            }
        )

    candidates.sort(key=lambda x: x["match_score"], reverse=True)
    return {"items": candidates[:20]}
