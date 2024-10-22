from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
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
    "/environments",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.EnvironmentResponse],
)
def get_all_environments(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    limit: int = 50,
    skip: int = 0,
    search: str | None = "",
    cloudprovider_id: int | None = None,
):
    """Get all environments in ascending order of name"""

    environments = db.scalars(
        select(models.Environment)
        .where(models.Environment.name.contains(search))
        # .where(models.Environment.active)
        .where(
            models.Environment.cloudprovider_id == cloudprovider_id
            if cloudprovider_id
            else models.Environment.cloudprovider_id != -1
        )
        .order_by(models.Environment.name)
        .limit(limit=limit)
        .offset(skip)
    ).all()

    if not environments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "ENVIRONMENT_NOT_FOUND",
                "module": "environments",
                "message": "The requested environment(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    for environment in environments:
        user = db.scalar(
            select(models.User).where(models.User.id == environment.created_by)
        )
        if user:
            environment.creator = user.email

    return environments


@json_router.get(
    "/environments/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.EnvironmentResponse,
)
def get_environment(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a environment by id"""

    environment = db.scalar(
        select(models.Environment).where(models.Environment.id == id)
    )

    if not environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "ENVIRONMENT_NOT_FOUND",
                "module": "environments",
                "message": "The requested environment(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    user = db.scalar(
        select(models.User).where(models.User.id == environment.created_by)
    )
    if user:
        environment.creator = user.email

    return environment


@json_router.post(
    path="/environments",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.EnvironmentResponse,
)
def create_environment(
    new_environment: schemas.EnvironmentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a environment"""

    # Check if the environment already exists, if yes, then raise an error
    environment = db.scalar(
        select(models.Environment).where(
            models.Environment.name == new_environment.name
        )
    )

    if environment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": "ENVIRONMENT_EXISTS",
                "module": "environments",
                "message": "The environment(s) you are trying to add already exist. Verify the details and try again.",
                "path": request.url.path,
            },
        )

    environment = models.Environment(
        **new_environment.model_dump(), created_by=current_user.id
    )
    db.add(environment)
    db.commit()
    db.refresh(instance=environment)
    environment.creator = current_user.email
    return environment


@json_router.delete(
    path="/environments/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_environment(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a environment"""

    environment = db.scalar(
        select(models.Environment).where(models.Environment.id == id)
    )

    if not environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "ENVIRONMENT_NOT_FOUND",
                "module": "environments",
                "message": "The requested environment(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    db.delete(environment)
    db.commit()


@json_router.put(
    path="/environments/{id}",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.EnvironmentResponse,
)
def update_environment(
    id: int,
    updated_environment: schemas.EnvironmentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a environment."""
    environment = db.scalar(
        select(models.Environment).where(models.Environment.id == id)
    )

    if not environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "ENVIRONMENT_NOT_FOUND",
                "module": "environments",
                "message": "The requested environment(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    for key, value in updated_environment.model_dump(
        exclude_unset=False, exclude_none=True
    ).items():
        setattr(environment, key, value)

    db.commit()
    db.refresh(instance=environment)
    user = db.scalar(
        select(models.User).where(models.User.id == environment.created_by)
    )
    if user:
        environment.creator = user.email
    return environment


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
    "/environments",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def hx_get_all_environments(
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    skip: int = 0,
    search: str | None = "",
    cloudprovider_id: int | None = None,
):
    try:
        environments = get_all_environments(
            limit=limit,
            skip=skip,
            search=search,
            cloudprovider_id=cloudprovider_id,
            request=request,
            current_user=current_user,
            db=db,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            environments = []
        else:
            raise e

    context = {
        "current_user": current_user,
        "environments": environments,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="environments/index.html",
        context=context,
    )

    return response


@html_router.get(
    "/environments/create",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_environment_create_form(
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    """Get a environment by id"""

    cloudproviders = db.scalars(select(models.CloudProvider)).all()

    context = {
        "current_user": current_user,
        "action": "create",
        "cloudproviders": cloudproviders,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="environments/crud.html",
        context=context,
    )

    return response


@html_router.get(
    "/environments/{id}/edit",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_edit_environment(
    id: int,
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    """Get a environment by id"""

    try:
        environment = get_environment(
            request=request,
            db=db,
            id=id,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            environment = None
        else:
            raise e

    context = {
        "current_user": current_user,
        "action": "update",
        "environment": environment,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="environments/crud.html",
        context=context,
    )

    return response


@html_router.get(
    "/environments/{id}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_get_environment(
    id: int,
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    """Get a environment by id"""

    try:
        environment = get_environment(
            request=request,
            db=db,
            id=id,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            environment = None
        else:
            raise e

    context = {
        "current_user": current_user,
        "action": "read",
        "environment": environment,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="environments/crud.html",
        context=context,
    )
    return response


# This route is for Cascading select when creating a deployment
@html_router.get(
    "/environments-cloudproviders",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def hx_get_environments_by_cloudprovider_id(
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
    cloudprovider_id: int | None = None,
):
    try:
        environments = get_all_environments(
            cloudprovider_id=cloudprovider_id,
            request=request,
            current_user=current_user,
            db=db,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            environments = []
        else:
            raise e

    context = {
        "current_user": current_user,
        "action": "create",
        "environments": environments,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="environments/environments-select.html",
        context=context,
    )

    return response


@html_router.post(
    path="/environments",
    status_code=status.HTTP_201_CREATED,
    response_class=HTMLResponse,
)
def hx_create_environment(
    request: Request,
    new_environment: schemas.EnvironmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Create a environment"""
    try:
        environment = create_environment(
            new_environment=new_environment,
            request=request,
            db=db,
            current_user=current_user,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            environment = None
        else:
            raise e

    context = {
        "current_user": current_user,
        "environment": environment,
        "request": request,
    }
    return templates.TemplateResponse(
        request=request,
        name="environments/card.html",
        context=context,
        status_code=status.HTTP_201_CREATED,
        headers={"HX-Trigger": "closeModal"},
    )


@html_router.delete(
    path="/environments/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=HTMLResponse,
)
def hx_delete_environment(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Delete a environment"""
    try:
        environment = delete_environment(
            id=id,
            request=request,
            db=db,
            current_user=current_user,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            environment = None
        else:
            raise e

    context = {
        "current_user": current_user,
        "environment": environment,
        "request": request,
    }
    return templates.TemplateResponse(
        request=request,
        name="shared/none.html",
        context=context,
        headers={"HX-Trigger": "closeModal"},
    )


@html_router.put(
    path="/environments/{id}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_update_environment(
    request: Request,
    id: int,
    updated_environment: schemas.EnvironmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Update a environment."""

    try:
        environment = update_environment(
            id=id,
            updated_environment=updated_environment,
            request=request,
            db=db,
            current_user=current_user,
        )
    except HTTPException as e:
        print(e)  # TODO: replace with logger
        context = {
            "current_user": current_user,
            "message": "An error occurred while updating the environment. Please try again.",
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
        "environment": environment,
        "request": request,
    }
    return templates.TemplateResponse(
        request=request,
        name="environments/crud.html",
        context=context,
    )


######## Validation Route ########


def hx_validate_environment_name(
    environment: schemas.EnvironmentValidate,
    db: Session = Depends(get_db),
):
    environment_exists = db.scalars(
        select(models.Environment).where(models.Environment.name == environment.name)
    ).first()
    if environment.name and len(environment.name) >= 3 and not environment_exists:
        return True
    return False


def hx_validate_environment_aws_account_id(
    environment: schemas.EnvironmentValidate,
    db: Session = Depends(get_db),
):
    if environment.aws_account_id and len(environment.aws_account_id) == 12:
        return True
    return False


def hx_validate_environment_aws_access_key_id(
    environment: schemas.EnvironmentValidate,
    db: Session = Depends(get_db),
):
    if environment.aws_access_key_id and len(environment.aws_access_key_id) >= 3:
        return True
    return False


def hx_validate_environment_aws_secret_access_key(
    environment: schemas.EnvironmentValidate,
    db: Session = Depends(get_db),
):
    if (
        environment.aws_secret_access_key
        and len(environment.aws_secret_access_key) >= 3
    ):
        return True
    return False


@html_router.post(
    "/environments/validate/{field}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def hx_validate_environment_create_form(
    environment: schemas.EnvironmentValidate,
    field: str,
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    name_is_valid = hx_validate_environment_name(
        environment,
        db,
    )

    aws_account_id_is_valid = hx_validate_environment_aws_account_id(
        environment,
        db,
    )
    aws_access_key_id_is_valid = hx_validate_environment_aws_access_key_id(
        environment,
        db,
    )
    aws_secret_access_key_is_valid = hx_validate_environment_aws_secret_access_key(
        environment,
        db,
    )

    enable_submit_btn = (
        name_is_valid
        and aws_account_id_is_valid
        and aws_access_key_id_is_valid
        and aws_secret_access_key_is_valid
    )

    if field == "name":
        context = {
            "field": "name",
            "is_validated": name_is_valid,
            "value": environment.name,
            "ready_to_submit": enable_submit_btn,
        }
    elif field == "aws_account_id":
        context = {
            "field": "aws_account_id",
            "is_validated": aws_account_id_is_valid,
            "value": environment.aws_account_id,
            "ready_to_submit": enable_submit_btn,
        }
    elif field == "aws_access_key_id":
        context = {
            "field": "aws_access_key_id",
            "is_validated": aws_access_key_id_is_valid,
            "value": environment.aws_access_key_id,
            "ready_to_submit": enable_submit_btn,
        }
    elif field == "aws_secret_access_key":
        context = {
            "field": "aws_secret_access_key",
            "is_validated": aws_secret_access_key_is_valid,
            "value": environment.aws_secret_access_key,
            "ready_to_submit": enable_submit_btn,
        }

    response = templates.TemplateResponse(
        request=request,
        name="environments/validate.html",
        context=context,
    )

    return response
