from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models import Group, GroupMember, User, Vote, VoteOption, VoteRecord
from app.schemas.groups import CreateGroupRequest, StartVoteRequest

router = APIRouter()


class CastGroupVoteRequest(BaseModel):
    routeId: int


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


@router.get("/{group_id:int}")
def get_group_detail(group_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    _ = user
    group = db.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    member_count = db.scalar(select(func.count(GroupMember.id)).where(GroupMember.group_id == group_id)) or 0
    return {
        "group_id": group.id,
        "name": group.name,
        "owner_user_id": group.owner_user_id,
        "city_code": group.city_code,
        "target_count": group.target_count,
        "threshold_count": group.threshold_count,
        "member_count": member_count,
        "status": group.status,
    }


@router.get("/my")
def list_my_groups(
    type: str = "joined",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    if type == "created":
        rows = db.scalars(select(Group).where(Group.owner_user_id == user.id).order_by(Group.id.desc())).all()
    else:
        rows = db.scalars(
            select(Group).join(GroupMember, GroupMember.group_id == Group.id).where(GroupMember.user_id == user.id).order_by(Group.id.desc())
        ).all()
    return {
        "items": [
            {"group_id": row.id, "name": row.name, "status": row.status, "target_count": row.target_count}
            for row in rows
        ]
    }


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


@router.post("/{group_id}/votes/sessions")
def start_vote_session_alias(
    group_id: int,
    payload: StartVoteRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return start_vote(group_id=group_id, payload=payload, db=db, user=user)


@router.post("/{group_id}/votes")
def cast_vote_by_group(
    group_id: int,
    payload: CastGroupVoteRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    vote = db.scalar(select(Vote).where(Vote.group_id == group_id).order_by(Vote.id.desc()))
    if not vote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote session not found")
    option = db.scalar(select(VoteOption).where(VoteOption.id == payload.routeId, VoteOption.vote_id == vote.id))
    if not option:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid routeId")
    existing = db.scalar(select(func.count()).select_from(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == user.id))
    if not existing:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only group members can vote")
    record = db.scalar(select(VoteRecord).where(VoteRecord.vote_id == vote.id, VoteRecord.user_id == user.id))
    if record:
        return {"vote_id": vote.id, "option_id": record.option_id}
    db.add(VoteRecord(vote_id=vote.id, option_id=payload.routeId, user_id=user.id))
    db.commit()
    return {"vote_id": vote.id, "option_id": payload.routeId}


@router.get("/{group_id}/votes/result")
def vote_result_by_group(group_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    _ = user
    vote = db.scalar(select(Vote).where(Vote.group_id == group_id).order_by(Vote.id.desc()))
    if not vote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote session not found")
    rows = db.execute(
        select(VoteRecord.option_id, func.count(VoteRecord.id))
        .where(VoteRecord.vote_id == vote.id)
        .group_by(VoteRecord.option_id)
        .order_by(func.count(VoteRecord.id).desc())
    ).all()
    stats = [{"option_id": row[0], "count": row[1]} for row in rows]
    winner_option_id = stats[0]["option_id"] if stats else None
    return {"vote_id": vote.id, "winner_option_id": winner_option_id, "stats": stats}


@router.get("/{group_id}/votes/sessions/current")
def get_current_vote_session(
    group_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    _ = user
    vote = db.scalar(select(Vote).where(Vote.group_id == group_id).order_by(Vote.id.desc()))
    if not vote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote session not found")
    options = db.scalars(select(VoteOption).where(VoteOption.vote_id == vote.id).order_by(VoteOption.id.asc())).all()
    return {
        "vote_id": vote.id,
        "status": vote.status,
        "start_time": vote.start_time,
        "end_time": vote.end_time,
        "options": [
            {"option_id": option.id, "title": option.title, "fee_estimate": float(option.fee_estimate)} for option in options
        ],
    }
