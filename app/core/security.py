from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings


def create_access_token(user_id: int, expires_hours: int = 24) -> str:
    expire_at = datetime.now(tz=timezone.utc) + timedelta(hours=expires_hours)
    payload = {"sub": str(user_id), "exp": expire_at}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
