from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.permissions import is_public_path, permission_allowed, resolve_permission
from app.core.security import decode_access_token
from app.database import SessionLocal
from app.models.user import User


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method.upper()

        if not path.startswith("/api") or is_public_path(path) or method == "OPTIONS":
            return await call_next(request)

        if path.startswith("/docs") or path.startswith("/openapi"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Требуется авторизация"})

        token = auth_header[7:].strip()
        payload = decode_access_token(token)
        if not payload or "sub" not in payload:
            return JSONResponse(status_code=401, content={"detail": "Недействительный токен"})

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == int(payload["sub"])).first()
            if not user or not user.is_active:
                return JSONResponse(status_code=401, content={"detail": "Пользователь не найден"})

            permission = resolve_permission(method, path)
            if not permission_allowed(user.role, permission):
                return JSONResponse(status_code=403, content={"detail": "Недостаточно прав"})

            request.state.user = user
        finally:
            db.close()

        return await call_next(request)
