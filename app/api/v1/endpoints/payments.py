from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models import Order, Payment

router = APIRouter()


class WechatNotifyRequest(BaseModel):
    out_trade_no: str
    wechat_txn_id: str
    success: bool = True


@router.post("/wechat/notify")
def wechat_notify(payload: WechatNotifyRequest, db: Session = Depends(get_db)) -> dict:
    payment = db.scalar(select(Payment).where(Payment.out_trade_no == payload.out_trade_no))
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

    if payment.status == "success":
        return {"status": "ok", "message": "already processed"}

    payment.wechat_txn_id = payload.wechat_txn_id
    payment.notify_raw = payload.model_dump()
    payment.status = "success" if payload.success else "failed"
    payment.paid_at = datetime.utcnow() if payload.success else None

    order = db.get(Order, payment.order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if payload.success:
        order.status = "paid"
        order.paid_at = datetime.utcnow()
    else:
        order.status = "unpaid"

    db.commit()
    return {"status": "ok"}
