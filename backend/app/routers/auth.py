from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.permissions import ALL_ROLES, ROLE_LABELS, get_role_permissions
from app.core.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.deps.auth import get_current_user, user_permissions
from app.models.user import User
from app.schemas.auth import (
    AuthUserResponse,
    LoginRequest,
    RoleInfo,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


def _auth_user(user: User) -> AuthUserResponse:
    return AuthUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        permissions=user_permissions(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username.strip()).first()
    if not user or not user.is_active or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    token = create_access_token(user_id=user.id, username=user.username, role=user.role)
    return TokenResponse(access_token=token, user=_auth_user(user))


@router.get("/me", response_model=AuthUserResponse)
def me(user: User = Depends(get_current_user)):
    return _auth_user(user)


@router.post("/logout")
def logout():
    return {"ok": True}


@router.get("/roles", response_model=list[RoleInfo])
def list_roles(_user: User = Depends(get_current_user)):
    return [
        RoleInfo(
            id=role,
            label_ru=ROLE_LABELS[role]["ru"],
            label_en=ROLE_LABELS[role]["en"],
            label_ka=ROLE_LABELS[role]["ka"],
            permissions=sorted(get_role_permissions(role)),
        )
        for role in ALL_ROLES
    ]


@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return db.query(User).order_by(User.full_name.asc()).all()


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    if data.role not in ALL_ROLES:
        raise HTTPException(status_code=400, detail="Неизвестная роль")
    if db.query(User).filter(User.username == data.username.strip()).first():
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    user = User(
        username=data.username.strip(),
        email=data.email,
        full_name=data.full_name.strip(),
        role=data.role,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if data.role is not None:
        if data.role not in ALL_ROLES:
            raise HTTPException(status_code=400, detail="Неизвестная роль")
        user.role = data.role
    if data.full_name is not None:
        user.full_name = data.full_name.strip()
    if data.email is not None:
        user.email = data.email
    if data.is_active is not None:
        if user.id == current.id and not data.is_active:
            raise HTTPException(status_code=400, detail="Нельзя деактивировать себя")
        user.is_active = data.is_active
    if data.password:
        user.hashed_password = hash_password(data.password)

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if user.id == current.id:
        raise HTTPException(status_code=400, detail="Нельзя удалить себя")
    db.delete(user)
    db.commit()
