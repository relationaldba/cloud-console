from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import oauth2, utils, verify_access_token
from app.config import settings, config
from app.database import get_db

AUTH_COOKIE_EXPIRE_MINUTES = settings.auth_token_expire_minutes


json_router = APIRouter()
html_router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


"""
    /*
     *
     *
     *      JSON Data API Routes
     *
     *
     */
"""


@json_router.post(
    path="/login",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Token,
)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login the user."""
    user = db.scalars(
        select(models.User)
        .where(models.User.email == user_credentials.username)
        .where(models.User.active)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="invalid credentials",
        )
    
    if not utils.verify_password(
        plain_password=user_credentials.password,
        hashed_password=user.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="invalid credentials",
        )

    access_token = oauth2.create_access_token(
        data={"username": user_credentials.username},
    )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(instance=user)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


"""
    /*
     *
     *
     *      Hypermedia (HTML) API Routes
     *
     *
     */
"""


@html_router.get(
    path="/login",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_login(
    request: Request,
    db: Session = Depends(get_db),
):
    """Login the user."""

    access_token = request.cookies.get("access_token")

    if access_token:
        token = access_token.split(" ")[1]
    else:
        token = None

    if token:
        try:
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

            response = RedirectResponse(
                url="/",
                status_code=status.HTTP_303_SEE_OTHER,
                headers={"HX-Refresh": "true"},
            )

            return response

        except HTTPException:
            pass

    # response.delete_cookie("access_token")

    context = {"current_user": None, "config": config}
    response = templates.TemplateResponse(
        request=request,
        name="login/login.html",
        context=context,
        headers={"HX-Refresh": "true"},
    )

    response.delete_cookie("access_token")

    return response


@html_router.post(
    path="/login",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_authenticate(
    request: Request,
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login the user."""

    try:
        login_context = login(user_credentials=user_credentials, db=db)

        response = RedirectResponse(
            url="/",
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"HX-Refresh": "true"},
        )

        access_token = login_context.get("access_token")
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            expires=datetime.now(timezone.utc)
            + timedelta(minutes=AUTH_COOKIE_EXPIRE_MINUTES),
            httponly=True,  # Cookie can't be accessed via JavaScript (prevents XSS attacks)
            samesite="lax",  # Cookie cannot be used in cross-site requests (prevents CSRF attacks)
            secure=True,  # Secure attribute to ensure the cookie is sent over HTTPS (prevents MITM attacks)
        )

        return response

    except HTTPException:
        context = {"authentication_failed": True, "config": config}
        response = templates.TemplateResponse(
            request=request,
            name="login/login.html",
            context=context,
            headers={"HX-Refresh": "true"},
            status_code=status.HTTP_303_SEE_OTHER,
        )
        response.delete_cookie("access_token")
        return response
