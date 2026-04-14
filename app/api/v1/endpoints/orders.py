from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models import Group, Order, Payment, User
from app.schemas.orders import CreateOrderRequest

router = APIRouter()


@router.post("/pay")
def create_pay_order(
    payload: CreateOrderRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    group = db.get(Group, payload.group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    existing = db.scalar(
        select(Order).where(Order.group_id == payload.group_id, Order.user_id == user.id, Order.status.in_(["unpaid", "paid"]))
    )
    if existing:
        return {"order_id": existing.id, "order_no": existing.order_no, "status": existing.status}

    amount = 99.0
    platform_fee = 12.0
    insurance_fee = 5.0
    order = Order(
        order_no=f"TM{uuid4().hex[:18]}",
        user_id=user.id,
        group_id=payload.group_id,
        amount=amount,
        platform_fee=platform_fee,
        insurance_fee=insurance_fee,
        status="unpaid",
        pay_deadline=datetime.utcnow() + timedelta(hours=24),
    )
    db.add(order)
    db.flush()

    payment = Payment(
        order_id=order.id,
        out_trade_no=f"WX{uuid4().hex[:20]}",
        amount=amount,
        status="pending",
    )
    db.add(payment)
    db.commit()
    return {
        "order_id": order.id,
        "order_no": order.order_no,
        "amount": float(order.amount),
        "mock_wechat_params": {"out_trade_no": payment.out_trade_no},
    }


@router.get("")
def list_orders(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    rows = db.scalars(select(Order).where(Order.user_id == user.id).order_by(Order.id.desc()).limit(50)).all()
    return {
        "items": [
            {
                "order_id": row.id,
                "order_no": row.order_no,
                "group_id": row.group_id,
                "amount": float(row.amount),
                "status": row.status,
            }
            for row in rows
        ]
    }


@router.post("/{order_id}/refund/apply")
def apply_refund(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    order = db.scalar(select(Order).where(Order.id == order_id, Order.user_id == user.id))
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.status != "paid":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only paid order can be refunded")
    order.status = "refunding"
    db.commit()
    return {"order_id": order.id, "status": order.status}
