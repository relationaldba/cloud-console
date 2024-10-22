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
    "/deployments",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.DeploymentResponse],
)
def get_all_deployments(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    limit: int = 50,
    skip: int = 0,
    search: str | None = "",
):
    """Get all deployments in ascending order of name"""

    deployments = db.scalars(
        select(models.Deployment)
        .where(models.Deployment.name.contains(search))
        # .where(models.Deployment.active)
        .order_by(models.Deployment.name)
        .limit(limit=limit)
        .offset(skip)
    ).all()

    if not deployments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "ENVIRONMENT_NOT_FOUND",
                "module": "deployments",
                "message": "The requested deployment(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    for deployment in deployments:
        user = db.scalar(
            select(models.User).where(models.User.id == deployment.created_by)
        )
        if user:
            deployment.creator = user.email

    return deployments


@json_router.get(
    "/deployments/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.DeploymentResponse,
)
def get_deployment(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a deployment by id"""

    deployment = db.scalar(select(models.Deployment).where(models.Deployment.id == id))

    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "ENVIRONMENT_NOT_FOUND",
                "module": "deployments",
                "message": "The requested deployment(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    user = db.scalar(select(models.User).where(models.User.id == deployment.created_by))
    if user:
        deployment.creator = user.email

    return deployment


@json_router.post(
    path="/deployments",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.DeploymentResponse,
)
def create_deployment(
    new_deployment: schemas.DeploymentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a deployment"""

    # Check if the deployment already exists, if yes, then raise an error
    deployment = db.scalar(
        select(models.Deployment).where(models.Deployment.name == new_deployment.name)
    )

    if deployment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": "ENVIRONMENT_EXISTS",
                "module": "deployments",
                "message": "The deployment(s) you are trying to add already exist. Verify the details and try again.",
                "path": request.url.path,
            },
        )

    deployment = models.Deployment(
        **new_deployment.model_dump(), created_by=current_user.id
    )
    db.add(deployment)
    db.commit()
    db.refresh(instance=deployment)
    deployment.creator = current_user.email
    return deployment


@json_router.delete(
    path="/deployments/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_deployment(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a deployment"""

    deployment = db.scalar(select(models.Deployment).where(models.Deployment.id == id))

    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "ENVIRONMENT_NOT_FOUND",
                "module": "deployments",
                "message": "The requested deployment(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    db.delete(deployment)
    db.commit()


@json_router.put(
    path="/deployments/{id}",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.DeploymentResponse,
)
def update_deployment(
    id: int,
    updated_deployment: schemas.DeploymentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a deployment."""
    deployment = db.scalar(select(models.Deployment).where(models.Deployment.id == id))

    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "ENVIRONMENT_NOT_FOUND",
                "module": "deployments",
                "message": "The requested deployment(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    for key, value in updated_deployment.model_dump(
        exclude_unset=False, exclude_none=True
    ).items():
        setattr(deployment, key, value)

    db.commit()
    db.refresh(instance=deployment)
    user = db.scalar(select(models.User).where(models.User.id == deployment.created_by))
    if user:
        deployment.creator = user.email
    return deployment


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
    "/deployments",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def hx_get_all_deployments(
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    skip: int = 0,
    search: str | None = "",
):
    try:
        deployments = get_all_deployments(
            limit=limit,
            skip=skip,
            search=search,
            request=request,
            current_user=current_user,
            db=db,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            deployments = []
        else:
            raise e

    context = {
        "current_user": current_user,
        "action": "read",
        "deployments": deployments,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="deployments/index.html",
        context=context,
    )

    return response


@html_router.get(
    "/deployments/create",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_deployment_create_form(
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    """Get a deployment by id"""
    cloudproviders = db.scalars(select(models.CloudProvider)).all()
    environments = db.scalars(select(models.Environment)).all()
    stacks = db.scalars(select(models.Stack)).all()

    context = {
        "current_user": current_user,
        "action": "create",
        "cloudproviders": cloudproviders,
        "environments": environments,
        "stacks": stacks,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="deployments/crud.html",
        context=context,
    )

    return response


@html_router.get(
    "/deployments/{id}/edit",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_edit_deployment(
    id: int,
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    """Get a deployment by id"""

    try:
        deployment = get_deployment(
            request=request,
            db=db,
            id=id,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            deployment = None
        else:
            raise e
        # TODO: Replace with logger

    context = {
        "current_user": current_user,
        "action": "update",
        "deployment": deployment,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="deployments/crud.html",
        context=context,
    )

    return response


@html_router.get(
    "/deployments/{id}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_get_deployment(
    id: int,
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    """Get a deployment by id"""

    try:
        deployment = get_deployment(
            request=request,
            db=db,
            id=id,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            deployment = None
        else:
            raise e

    context = {
        "current_user": current_user,
        "action": "read",
        "deployment": deployment,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="deployments/crud.html",
        context=context,
    )
    return response


@html_router.post(
    path="/deployments",
    status_code=status.HTTP_201_CREATED,
    response_class=HTMLResponse,
)
def hx_create_deployment(
    request: Request,
    new_deployment: schemas.DeploymentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Create a deployment"""
    try:
        deployment = create_deployment(
            new_deployment=new_deployment,
            request=request,
            db=db,
            current_user=current_user,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            deployment = None
        else:
            raise e

    context = {
        "current_user": current_user,
        "deployment": deployment,
        "request": request,
    }
    return templates.TemplateResponse(
        request=request,
        name="deployments/card.html",
        context=context,
        status_code=status.HTTP_201_CREATED,
        headers={"HX-Trigger": "closeModal"},
    )


@html_router.delete(
    path="/deployments/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=HTMLResponse,
)
def hx_delete_deployment(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Delete a deployment"""
    try:
        deployment = delete_deployment(
            id=id,
            request=request,
            db=db,
            current_user=current_user,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            deployment = None
        else:
            raise e

    context = {
        "current_user": current_user,
        "deployment": deployment,
        "request": request,
    }
    return templates.TemplateResponse(
        request=request,
        name="shared/none.html",
        context=context,
        headers={"HX-Trigger": "closeModal"},
    )


@html_router.put(
    path="/deployments/{id}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_update_deployment(
    request: Request,
    id: int,
    updated_deployment: schemas.DeploymentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Update a deployment."""

    try:
        deployment = update_deployment(
            id=id,
            updated_deployment=updated_deployment,
            request=request,
            db=db,
            current_user=current_user,
        )
    except HTTPException as e:
        print(e)  # TODO: replace with logger
        context = {
            "current_user": current_user,
            "message": "An error occurred while updating the deployment. Please try again.",
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
        "deployment": deployment,
        "request": request,
    }
    return templates.TemplateResponse(
        request=request,
        name="deployments/crud.html",
        context=context,
    )


######## Validation Route ########


def hx_validate_deployment_name(
    deployment: schemas.DeploymentValidate,
    db: Session = Depends(get_db),
):
    deployment_exists = db.scalars(
        select(models.Deployment).where(models.Deployment.name == deployment.name)
    ).first()
    if deployment.name and len(deployment.name) >= 3 and not deployment_exists:
        return True
    return False


@html_router.post(
    "/deployments/validate/{field}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def hx_validate_deployment_create_form(
    deployment: schemas.DeploymentValidate,
    field: str,
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    name_is_valid = hx_validate_deployment_name(
        deployment,
        db,
    )

    enable_submit_btn = name_is_valid

    if field == "name":
        context = {
            "field": "name",
            "is_validated": name_is_valid,
            "value": deployment.name,
            "ready_to_submit": enable_submit_btn,
        }
        print("Hi there")

    response = templates.TemplateResponse(
        request=request,
        name="deployments/validate.html",
        context=context,
    )

    return response
