from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.security import create_access_token
from app.models import User, UserProfile
from app.schemas.auth import LoginResponse, WechatLoginRequest

router = APIRouter()


@router.post("/wechat/login")
def wechat_login(payload: WechatLoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    wechat_openid = f"mock_{payload.code}"
    user = db.scalar(select(User).where(User.wechat_openid == wechat_openid))
    is_new_user = False
    if not user:
        is_new_user = True
        user = User(
            wechat_openid=wechat_openid,
            nickname=payload.nickname or f"user_{payload.code[-6:]}",
            avatar_url=payload.avatar_url,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    profile_exists = db.scalar(select(UserProfile).where(UserProfile.user_id == user.id)) is not None
    token = create_access_token(user.id)
    return LoginResponse(
        access_token=token,
        token=token,
        user_id=user.id,
        userId=user.id,
        profile_completed=profile_exists,
        isNewUser=is_new_user,
    )


@router.post("/logout")
def logout(_: User = Depends(get_current_user)) -> dict:
    return {"message": "ok"}
