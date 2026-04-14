from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models import User, UserProfile
from app.schemas.users import PersonalityTestRequest

router = APIRouter()

QUESTION_BANK = [
    {"question_id": 1, "title": "旅行节奏", "options": [{"option_id": 1, "label": "早鸟型"}, {"option_id": 2, "label": "睡到自然醒"}]},
    {"question_id": 2, "title": "旅行强度", "options": [{"option_id": 1, "label": "特种兵"}, {"option_id": 2, "label": "躺平派"}]},
    {"question_id": 3, "title": "旅行偏好", "options": [{"option_id": 1, "label": "出片狂魔"}, {"option_id": 2, "label": "深度体验"}]},
    {"question_id": 4, "title": "饮食偏好", "options": [{"option_id": 1, "label": "当地特色"}, {"option_id": 2, "label": "家常菜"}]},
    {"question_id": 5, "title": "同行偏好", "options": [{"option_id": 1, "label": "安静独处"}, {"option_id": 2, "label": "热闹互动"}]},
]


@router.get("/questions")
def list_questions() -> dict:
    return {"items": QUESTION_BANK}


@router.post("/submissions")
def submit_dna(
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
    return {"dnaType": "+".join(tags[:3]), "tags": tags, "preferences": {"pace": tags[0] if tags else None}}


@router.get("/me/latest")
def get_latest_dna(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    tags = (profile.tags_json or {}).get("tags", []) if profile else []
    return {"user_id": user.id, "tags": tags, "personality_test_done": bool(profile and profile.personality_test_done)}
