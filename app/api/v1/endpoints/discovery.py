from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models import Group

router = APIRouter()


@router.get("/groups")
def list_discovery_groups(db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(Group).where(Group.status == "recruiting").order_by(Group.id.desc()).limit(50)).all()
    return {
        "items": [
            {
                "group_id": row.id,
                "name": row.name,
                "city_code": row.city_code,
                "target_count": row.target_count,
                "status": row.status,
            }
            for row in rows
        ]
    }
