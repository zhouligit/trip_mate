from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models import User, UserProfile
from app.schemas.users import PersonalityTestRequest, UpdateLocationRequest, UpdateMeRequest

router = APIRouter()


@router.get("/me")
def get_me(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    return {
        "userId": user.id,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "mobile": user.mobile,
        "realname_verified": bool(user.realname_verified),
        "profile_completed": bool(profile and profile.personality_test_done),
    }


@router.put("/me")
def update_me(
    payload: UpdateMeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    if payload.nickname is not None:
        user.nickname = payload.nickname
    if payload.avatar_url is not None:
        user.avatar_url = payload.avatar_url
    if payload.mobile is not None:
        user.mobile = payload.mobile
    db.commit()
    return {"userId": user.id, "nickname": user.nickname, "avatar_url": user.avatar_url, "mobile": user.mobile}


@router.post("/personality-test")
def submit_personality_test(
    payload: PersonalityTestRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    tags = [f"q{item.question_id}_o{item.option_id}" for item in payload.answers[:5]]
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    if not profile:
        profile = UserProfile(
            user_id=user.id,
            city_code="unknown",
            tags_json={"tags": tags},
            personality_test_done=1,
        )
        db.add(profile)
    else:
        profile.tags_json = {"tags": tags}
        profile.personality_test_done = 1
    db.commit()
    return {"tags": tags}


@router.post("/location")
def update_location(
    payload: UpdateLocationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    if not profile:
        profile = UserProfile(
            user_id=user.id,
            city_code=payload.city_code,
            district_code=payload.district_code,
            tags_json={"tags": []},
            personality_test_done=0,
        )
        db.add(profile)
    else:
        profile.city_code = payload.city_code
        profile.district_code = payload.district_code
    db.commit()
    return {"city_code": payload.city_code, "district_code": payload.district_code}
