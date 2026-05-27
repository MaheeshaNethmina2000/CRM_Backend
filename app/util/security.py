import hashlib
from datetime import datetime, timedelta, timezone
from typing import Callable, Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.exc import MissingBackendError
from sqlalchemy.orm import Session

from app.config.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from app.config.database_config import get_database
from app.enums.enums import UserRole

_password_contexts = {
    "bcrypt": CryptContext(schemes=["bcrypt"], deprecated="auto"),
    "pbkdf2": CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto"),
}

bearer_scheme = HTTPBearer()


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


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_database),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
    )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        token_type = payload.get("type")
        if token_type != "access":
            raise credentials_exception
        user_id = payload.get("sub")
    except (JWTError, TypeError, ValueError):
        raise credentials_exception

    # TODO: inject your UserRepository here
    # user_repo = UserRepository()
    # user = user_repo.get_by_uuid(user_id, db)
    # if not user:
    #     raise credentials_exception
    # return user
    return user_id


def require_roles(roles: Iterable[UserRole]) -> Callable:
    def _role_checker(current_user=Depends(get_current_user)):
        # TODO: check current_user.role against roles
        return current_user

    return _role_checker
