from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models import User
from app.schemas.verification import IdcardVerificationRequest, WechatVerificationRequest

router = APIRouter()


@router.get("/me/status")
def get_verification_status(user: User = Depends(get_current_user)) -> dict:
    return {"userId": user.id, "realname_verified": bool(user.realname_verified), "status": "verified" if user.realname_verified else "unverified"}


@router.post("/wechat")
def verify_by_wechat(
    payload: WechatVerificationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    _ = payload
    user.realname_verified = 1
    db.commit()
    return {"userId": user.id, "realname_verified": True, "channel": "wechat"}


@router.post("/idcard")
def verify_by_idcard(
    payload: IdcardVerificationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    _ = payload
    user.realname_verified = 1
    db.commit()
    return {"userId": user.id, "realname_verified": True, "channel": "idcard"}
