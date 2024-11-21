import re
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.auth import get_current_user, hx_get_current_user
from app.database import get_db

html_router = APIRouter()
json_router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

"""
    /*
     *
     *
     *      JSON Data API Routes (GET, POST, PUT, DELETE)
     *
     *
     */
"""


@json_router.get(
    "/users",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.UserResponse],
)
def get_all_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    limit: int = 50,
    skip: int = 0,
    search: str | None = "",
):
    """Get all users in ascending order of name"""

    users = db.scalars(
        select(models.User)
        .where(models.User.first_name.contains(search))
        # .where(models.User.active)
        .order_by(models.User.first_name)
        .limit(limit=limit)
        .offset(skip)
    ).all()

    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "USER_NOT_FOUND",
                "module": "users",
                "message": "The requested user(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    return users


@json_router.get(
    path="/users/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserResponse,
)
def get_user(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a User by id"""

    user = db.scalar(select(models.User).where(models.User.id == id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "USER_NOT_FOUND",
                "module": "users",
                "message": "The requested user(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    return user


@json_router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserResponse,
)
def create_user(
    new_user: schemas.UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a User"""

    user = db.scalar(select(models.User).where(models.User.email == new_user.email))

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": "USER_EXISTS",
                "module": "users",
                "message": "The user(s) you are trying to add already exist. Verify the details and try again.",
                "path": request.url.path,
            },
        )

    # Encrypt the password
    hashed_password = auth.hash_password(new_user.password)
    new_user.password = hashed_password

    user = models.User(**new_user.model_dump())

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@json_router.delete(
    path="/users/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a user"""

    user = db.scalar(select(models.User).where(models.User.id == id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "USER_NOT_FOUND",
                "module": "users",
                "message": "The requested user(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    db.delete(user)
    db.commit()


@json_router.put(
    path="/users/{id}",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserResponse,
)
def update_user(
    id: int,
    updated_user: schemas.UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a user."""
    user = db.scalar(select(models.User).where(models.User.id == id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "USER_NOT_FOUND",
                "module": "users",
                "message": "The requested user(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    # Encrypt the password
    if updated_user.password:
        hashed_password = auth.hash_password(updated_user.password)
        updated_user.password = hashed_password

    for key, value in updated_user.model_dump(
        exclude_unset=False, exclude_none=True
    ).items():
        setattr(user, key, value)

    db.commit()
    db.refresh(instance=user)
    return user


"""
    /*
     *
     *
     *      Hypermedia (HTML) API Routes (GET, POST, PUT, DELETE)
     *
     *
     */
"""


@html_router.get(
    "/users",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def hx_get_all_users(
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    skip: int = 0,
    search: str | None = "",
):
    try:
        users = get_all_users(
            limit=limit,
            skip=skip,
            search=search,
            request=request,
            current_user=current_user,
            db=db,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            users = []
        else:
            raise e

    context = {
        "current_user": current_user,
        "action": "read",
        "users": users,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="users/index.html",
        context=context,
    )

    return response


@html_router.get(
    "/users/create",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_user_create_form(
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    """Get a user by id"""

    context = {
        "current_user": current_user,
        "action": "create",
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="users/crud.html",
        context=context,
    )

    return response


@html_router.get(
    "/users/{id}/edit",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_edit_user(
    id: int,
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    """Get a user by id"""

    try:
        user = get_user(
            request=request,
            db=db,
            id=id,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            user = None
        else:
            raise e
        # TODO: Replace with logger

    context = {
        "current_user": current_user,
        "action": "update",
        "user": user,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="users/crud.html",
        context=context,
    )

    return response


@html_router.get(
    "/users/{id}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_get_user(
    id: int,
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    """Get a user by id"""

    try:
        user = get_user(
            request=request,
            db=db,
            id=id,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            user = None
        else:
            raise e

    context = {
        "current_user": current_user,
        "action": "read",
        "user": user,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="users/crud.html",
        context=context,
    )
    return response


@html_router.post(
    path="/users",
    status_code=status.HTTP_201_CREATED,
    response_class=HTMLResponse,
)
def hx_create_user(
    request: Request,
    new_user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Create a user"""
    try:
        user = create_user(
            new_user=new_user,
            request=request,
            db=db,
            current_user=current_user,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_409_CONFLICT:
            user = None
        else:
            raise e

    context = {
        "current_user": current_user,
        "user": user,
        "request": request,
    }
    return templates.TemplateResponse(
        request=request,
        name="users/card.html",
        context=context,
        status_code=status.HTTP_201_CREATED,
        headers={"HX-Trigger": "closeModal"},
    )


@html_router.delete(
    path="/users/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=HTMLResponse,
)
def hx_delete_user(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Delete a user"""
    try:
        user = delete_user(
            id=id,
            request=request,
            db=db,
            current_user=current_user,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            user = None
        else:
            raise e

    context = {
        "current_user": current_user,
        "user": user,
        "request": request,
    }
    return templates.TemplateResponse(
        request=request,
        name="shared/none.html",
        context=context,
        headers={"HX-Trigger": "closeModal"},
    )


@html_router.put(
    path="/users/{id}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_update_user(
    request: Request,
    id: int,
    updated_user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Update a user."""

    try:
        user = update_user(
            id=id,
            updated_user=updated_user,
            request=request,
            db=db,
            current_user=current_user,
        )
    except HTTPException as e:
        print(e)  # TODO: replace with logger
        context = {
            "current_user": current_user,
            "message": "An error occurred while updating the user. Please try again.",
            "request": request,
        }
        return templates.TemplateResponse(
            request=request,
            name="shared/error-message.html",
            headers={"HX-Reswap": "none"},
        )

    context = {
        "current_user": current_user,
        "action": "read",
        "user": user,
        "request": request,
    }
    return templates.TemplateResponse(
        request=request,
        name="users/crud.html",
        context=context,
    )


######## Validation Route ########


def hx_validate_user_first_name(
    user: schemas.UserValidate,
    db: Session = Depends(get_db),
):
    if user.first_name and len(user.first_name) >= 3:
        return True
    return False


def hx_validate_user_last_name(
    user: schemas.UserValidate,
    db: Session = Depends(get_db),
):
    if user.last_name and len(user.last_name) >= 3:
        return True
    return False


def hx_validate_user_email(
    user: schemas.UserValidate,
    db: Session = Depends(get_db),
):
    user_exists = db.scalars(
        select(models.User).where(models.User.email == user.email)
    ).first()

    regex = re.compile(
        r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
    )
    email_is_valid = regex.match(user.email) # type: ignore

    if user.email and email_is_valid and not user_exists:
        return True
    return False


def hx_validate_user_password(
    user: schemas.UserValidate,
    db: Session = Depends(get_db),
):
    regex = re.compile(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,18}$"
    )
    password_is_valid = regex.match(user.password) # type: ignore

    if user.password and password_is_valid:
        return True
    return False


@html_router.post(
    "/users/validate/{field}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def hx_validate_user_create_form(
    user: schemas.UserValidate,
    field: str,
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    first_name_is_valid = hx_validate_user_first_name(
        user,
        db,
    )
    last_name_is_valid = hx_validate_user_last_name(
        user,
        db,
    )
    email_is_valid = hx_validate_user_email(
        user,
        db,
    )
    password_is_valid = hx_validate_user_password(
        user,
        db,
    )

    enable_submit_btn = (
        first_name_is_valid
        and last_name_is_valid
        and email_is_valid
        and password_is_valid
    )

    if field == "first_name":
        context = {
            "field": "first_name",
            "is_validated": first_name_is_valid,
            "value": user.first_name,
            "ready_to_submit": enable_submit_btn,
        }

    elif field == "last_name":
        context = {
            "field": "last_name",
            "is_validated": last_name_is_valid,
            "value": user.last_name,
            "ready_to_submit": enable_submit_btn,
        }

    elif field == "email":
        context = {
            "field": "email",
            "is_validated": email_is_valid,
            "value": user.email,
            "ready_to_submit": enable_submit_btn,
        }

    elif field == "password":
        context = {
            "field": "password",
            "is_validated": password_is_valid,
            "value": user.password,
            "ready_to_submit": enable_submit_btn,
        }

    response = templates.TemplateResponse(
        request=request,
        name="users/validate.html",
        context=context,
    )

    return response
