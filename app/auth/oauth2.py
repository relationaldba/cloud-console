import datetime as dt
from typing import Annotated

import jwt
from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.config import settings
from app.database import get_db

SECRET_KEY = settings.auth_secret_key
ALGORITHM = settings.auth_algorithm
AUTH_TOKEN_EXPIRE_MINUTES = settings.auth_token_expire_minutes
AUTH_COOKIE_EXPIRE_MINUTES = settings.auth_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = dt.datetime.now(dt.timezone.utc) + dt.timedelta(
        minutes=AUTH_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception: HTTPException):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        username: str = payload.get("username")
        expiration: int = payload.get("exp")

        if username is None:
            raise credentials_exception

        token_data = schemas.TokenData(username=username, expiration=expiration)

    except InvalidTokenError:
        raise credentials_exception

    return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(
        token=token,
        credentials_exception=credentials_exception,
    )

    user: schemas.UserResponse = db.scalars(
        select(models.User)
        .where(models.User.email == token_data.username)
        .where(models.User.active)
    ).first()

    if user is None:
        raise credentials_exception

    return user


def hx_get_current_user(
    access_token: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if access_token:
        access_token = access_token.split(" ")[1]

    if access_token is None or not access_token:
        raise credentials_exception

    token_data = verify_access_token(
        token=access_token,
        credentials_exception=credentials_exception,
    )

    user = db.scalars(
        select(models.User)
        .where(models.User.email == token_data.username)
        .where(models.User.active)
    ).first()

    if user is None:
        raise credentials_exception

    return user


"""
def hx_get_current_user_home(
    access_token: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db),
):
    # credentials_exception = NotAuthenticatedException()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if access_token:
        access_token = access_token.split(" ")[1]

    if access_token is None or not access_token:
        # raise credentials_exception
        return None

    try:
        token_data = verify_access_token(token=access_token, credentials_exception=credentials_exception,)
    except HTTPException:
        return None

    if token_data is None or not token_data:
        # raise credentials_exception
        return None

    user = db.scalars(
        select(models.User)
        .where(models.User.email == token_data.username)
        .where(models.User.active)
    ).first()

    if user is None:
        return None

    return user
"""
