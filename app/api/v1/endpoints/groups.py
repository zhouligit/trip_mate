from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models import Group, GroupMember, User, Vote, VoteOption
from app.schemas.groups import CreateGroupRequest, StartVoteRequest

router = APIRouter()


@router.post("")
def create_group(
    payload: CreateGroupRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    group = Group(
        owner_user_id=user.id,
        name=payload.name,
        city_code=payload.city_code,
        target_count=payload.target_count,
        threshold_count=payload.threshold_count,
        status="recruiting",
    )
    db.add(group)
    db.flush()
    db.add(GroupMember(group_id=group.id, user_id=user.id, role="owner"))
    db.commit()
    return {"group_id": group.id, "status": group.status}


@router.post("/{group_id}/join")
def join_group(
    group_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    group = db.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    count_stmt = select(func.count(GroupMember.id)).where(GroupMember.group_id == group_id)
    current_count = db.scalar(count_stmt) or 0
    if current_count >= group.target_count:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group is full")

    member = db.scalar(
        select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == user.id)
    )
    if member:
        return {"group_id": group_id, "joined": True}

    db.add(GroupMember(group_id=group_id, user_id=user.id, role="member"))
    db.commit()
    return {"group_id": group_id, "joined": True}


@router.post("/{group_id}/vote/start")
def start_vote(
    group_id: int,
    payload: StartVoteRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    group = db.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    if group.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can start vote")

    existing_vote = db.scalar(select(Vote).where(Vote.group_id == group_id))
    if existing_vote:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vote already exists")

    now = datetime.utcnow()
    vote = Vote(group_id=group_id, start_time=now, end_time=now + timedelta(hours=payload.duration_hours))
    db.add(vote)
    db.flush()

    options = [
        VoteOption(
            vote_id=vote.id,
            title="古镇打卡+咖啡馆",
            route_desc="轻松拍照路线，含农家乐午餐",
            duration_desc="08:00-18:00",
            meetup_points_json={"points": ["地铁A口", "地铁B口"]},
            fee_estimate=79.0,
        ),
        VoteOption(
            vote_id=vote.id,
            title="海景露营+烧烤",
            route_desc="海边轻户外，傍晚返程",
            duration_desc="09:00-19:00",
            meetup_points_json={"points": ["地铁C口", "地铁D口"]},
            fee_estimate=99.0,
        ),
        VoteOption(
            vote_id=vote.id,
            title="文创街区+下午茶",
            route_desc="慢节奏逛街路线，适合社交",
            duration_desc="10:00-18:00",
            meetup_points_json={"points": ["地铁E口", "地铁F口"]},
            fee_estimate=69.0,
        ),
    ]
    db.add_all(options)

    group.status = "voting"
    group.vote_deadline = vote.end_time
    db.commit()
    return {"vote_id": vote.id, "group_status": group.status}
