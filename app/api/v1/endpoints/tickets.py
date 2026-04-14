from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models import Order, Ticket, User

router = APIRouter()


class GenerateTicketRequest(BaseModel):
    order_id: int


class VerifyTicketRequest(BaseModel):
    ticket_code: str


@router.post("/generate")
def generate_ticket(
    payload: GenerateTicketRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    order = db.scalar(select(Order).where(Order.id == payload.order_id, Order.user_id == user.id))
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.status != "paid":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only paid orders can generate tickets")

    ticket = db.scalar(select(Ticket).where(Ticket.order_id == order.id, Ticket.user_id == user.id))
    if not ticket:
        ticket_no = f"TK{uuid4().hex[:18]}"
        ticket = Ticket(
            ticket_no=ticket_no,
            order_id=order.id,
            user_id=user.id,
            group_id=order.group_id,
            qr_code=ticket_no,
            status="issued",
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
    return {"ticket_id": ticket.id, "ticket_no": ticket.ticket_no, "ticket_code": ticket.qr_code, "status": ticket.status}


@router.post("/verify")
def verify_ticket(payload: VerifyTicketRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> dict:
    ticket = db.scalar(select(Ticket).where(Ticket.qr_code == payload.ticket_code))
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    if ticket.status == "verified":
        return {"ticket_id": ticket.id, "verified": True, "verify_time": ticket.verify_time}
    ticket.status = "verified"
    ticket.verify_time = datetime.utcnow()
    db.commit()
    return {"ticket_id": ticket.id, "verified": True, "verify_time": ticket.verify_time}
