import hashlib
from datetime import datetime, timedelta, timezone
from typing import Callable, Iterable
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.exc import MissingBackendError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from app.config.database_config import get_database
from app.enums.enums import UserRole
from app.repository.staff_repository import StaffRepository
from app.exceptions.exception import UnauthorizedException, ForbiddenException

_password_contexts = {
    "bcrypt": CryptContext(schemes=["bcrypt"], deprecated="auto"),
    "pbkdf2": CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto"),
}

bearer_scheme = HTTPBearer()
staff_repository = StaffRepository()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    for context in _password_contexts.values():
        try:
            return context.verify(plain_password, hashed_password)
        except (MissingBackendError, ValueError):
            continue
    return False


def get_password_hash(password: str) -> str:
    # Use pbkdf2 for new hashes to avoid bcrypt's 72-byte password limit.
    return _password_contexts["pbkdf2"].hash(password)


def _access_exp_minutes() -> int:
    return int(ACCESS_TOKEN_EXPIRE_MINUTES)


def _refresh_exp_days() -> int:
    return int(REFRESH_TOKEN_EXPIRE_DAYS)


def create_token(user_id: str, token_type: str, expires_delta: timedelta) -> str:
    to_encode = {
        "sub": str(user_id),
        "type": token_type,
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_access_token(user_id: str) -> str:
    return create_token(user_id, "access", timedelta(minutes=_access_exp_minutes()))


def create_refresh_token(user_id: str) -> str:
    return create_token(user_id, "refresh", timedelta(days=_refresh_exp_days()))


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: AsyncSession = Depends(get_database),
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        token_type = payload.get("type")
        if token_type != "access":
            raise UnauthorizedException(message="Invalid token type provided.")

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise UnauthorizedException(message="Token payload is missing user identification.")

        # Safely convert the string back to a UUID for database querying
        user_id = UUID(user_id_str)

    except (JWTError, TypeError, ValueError):
        raise UnauthorizedException(message="Invalid authentication credentials.")

    # Await the async database call using your repository
    user = await staff_repository.get_by_id(user_id, db)

    if not user:
        raise UnauthorizedException(message="Authenticated user no longer exists.")

    if not user.is_active:
        raise UnauthorizedException(message="This user account has been deactivated.")

    return user


def require_roles(roles: Iterable[UserRole]) -> Callable:
    """
    Dependency generator to restrict route access based on UserRole enums.
    Usage in route: Depends(require_roles([UserRole.MANAGER, UserRole.SYSTEM_ADMIN]))
    """

    async def _role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in roles:
            raise ForbiddenException(message="You do not have the required permissions to access this resource.")
        return current_user

    return _role_checker