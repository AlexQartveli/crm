from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.permissions import get_role_permissions, has_permission
from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User


def _extract_token(request: Request) -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip()
    return None


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = _extract_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="Требуется авторизация")

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Недействительный токен")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Пользователь не найден или деактивирован")
    return user


def require_permission(permission: str):
    def checker(user: User = Depends(get_current_user)) -> User:
        if not has_permission(user.role, permission):
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        return user
    return checker


def user_permissions(user: User) -> list[str]:
    return sorted(get_role_permissions(user.role))
