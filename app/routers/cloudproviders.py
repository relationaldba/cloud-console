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
    "/cloudproviders",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.CloudProviderResponse],
)
def get_all_cloudproviders(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    limit: int = 50,
    skip: int = 0,
    search: str | None = "",
):
    """Get all Cloud Providers in ascending order of name"""

    cloudproviders = db.scalars(
        select(models.CloudProvider)
        .where(models.CloudProvider.name.contains(search))
        # .where(models.CloudProvider.active)
        .order_by(models.CloudProvider.name)
        .limit(limit=limit)
        .offset(skip)
    ).all()

    if cloudproviders is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "CLOUD_PROVIDER_NOT_FOUND",
                "module": "CloudProviders",
                "message": "The requested CloudProvider(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )
    for cloudprovider in cloudproviders:
        user = db.scalar(
            select(models.User).where(models.User.id == cloudprovider.created_by)
        )
        if user:
            cloudprovider.creator = user.email

    return cloudproviders


@json_router.get(
    "/cloudproviders/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.CloudProviderResponse,
)
def get_cloudprovider(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a cloudprovider by id"""

    cloudprovider = db.scalar(
        select(models.CloudProvider).where(models.CloudProvider.id == id)
    )

    if cloudprovider is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "CLOUD_PROVIDER_NOT_FOUND",
                "module": "CloudProviders",
                "message": "The requested CloudProvider(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    user = db.scalar(
        select(models.User).where(models.User.id == cloudprovider.created_by)
    )
    if user:
        cloudprovider.creator = user.email

    return cloudprovider


@json_router.post(
    path="/cloudproviders",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.CloudProviderResponse,
)
def create_cloudprovider(
    new_cloudprovider: schemas.CloudProviderCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a cloudprovider"""

    # Check if the cloudprovider already exists, if yes, then raise an error
    cloudprovider = db.scalar(
        select(models.CloudProvider).where(
            models.CloudProvider.name == new_cloudprovider.name
        )
    )

    if cloudprovider:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": "CLOUD_PROVIDER_EXISTS",
                "module": "CloudProviders",
                "message": "The cloudprovider(s) you are trying to add already exist. Verify the details and try again.",
                "path": request.url.path,
            },
        )

    cloudprovider = models.CloudProvider(
        **new_cloudprovider.model_dump(), created_by=current_user.id
    )
    db.add(cloudprovider)
    db.commit()
    db.refresh(instance=cloudprovider)
    cloudprovider.creator = current_user.email
    return cloudprovider


@json_router.delete(
    path="/cloudproviders/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_cloudprovider(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a cloudprovider"""

    cloudprovider = db.scalar(
        select(models.CloudProvider).where(models.CloudProvider.id == id)
    )

    if not cloudprovider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "CLOUD_PROVIDER_NOT_FOUND",
                "module": "CloudProviders",
                "message": "The requested CloudProvider(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    db.delete(cloudprovider)
    db.commit()


@json_router.put(
    path="/cloudproviders/{id}",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.CloudProviderResponse,
)
def update_cloudprovider(
    id: int,
    updated_cloudprovider: schemas.CloudProviderUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a cloudprovider."""
    cloudprovider = db.scalar(
        select(models.CloudProvider).where(models.CloudProvider.id == id)
    )

    if not cloudprovider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "CLOUD_PROVIDER_NOT_FOUND",
                "module": "CloudProviders",
                "message": "The requested CloudProvider(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    for key, value in updated_cloudprovider.model_dump(
        exclude_unset=False, exclude_none=True
    ).items():
        setattr(cloudprovider, key, value)

    db.commit()
    db.refresh(instance=cloudprovider)
    user = db.scalar(
        select(models.User).where(models.User.id == cloudprovider.created_by)
    )
    if user:
        cloudprovider.creator = user.email
    return cloudprovider


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
    "/cloudproviders",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def hx_get_all_cloudproviders(
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    skip: int = 0,
    search: str | None = "",
):
    try:
        cloudproviders = get_all_cloudproviders(
            limit=limit,
            skip=skip,
            search=search,
            request=request,
            current_user=current_user,
            db=db,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            cloudproviders = []
        else:
            raise e

    context = {
        "current_user": current_user,
        "action": "read",
        "cloudproviders": cloudproviders,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="cloudproviders/index.html",
        context=context,
    )

    return response


@html_router.get(
    "/cloudproviders/create",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_cloudprovider_create_form(
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    """Get a cloudprovider by id"""

    context = {
        "current_user": current_user,
        "action": "create",
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="cloudproviders/crud.html",
        context=context,
    )

    return response


@html_router.get(
    "/cloudproviders/{id}/edit",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_edit_cloudprovider(
    id: int,
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    """Get a cloudprovider by id"""

    try:
        cloudprovider = get_cloudprovider(
            request=request,
            db=db,
            id=id,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            cloudprovider = None
        else:
            raise e
        # TODO: Replace with logger

    context = {
        "current_user": current_user,
        "action": "update",
        "cloudprovider": cloudprovider,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="cloudproviders/crud.html",
        context=context,
    )

    return response


@html_router.get(
    "/cloudproviders/{id}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_get_cloudprovider(
    id: int,
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    """Get a cloudprovider by id"""

    try:
        cloudprovider = get_cloudprovider(
            request=request,
            db=db,
            id=id,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            cloudprovider = None
        else:
            raise e

    context = {
        "current_user": current_user,
        "action": "read",
        "cloudprovider": cloudprovider,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="cloudproviders/crud.html",
        context=context,
    )
    return response


@html_router.post(
    path="/cloudproviders",
    status_code=status.HTTP_201_CREATED,
    response_class=HTMLResponse,
)
def hx_create_cloudprovider(
    request: Request,
    new_cloudprovider: schemas.CloudProviderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Create a cloudprovider"""
    try:
        cloudprovider = create_cloudprovider(
            new_cloudprovider=new_cloudprovider,
            request=request,
            db=db,
            current_user=current_user,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            cloudprovider = None
        else:
            raise e

    context = {
        "current_user": current_user,
        "cloudprovider": cloudprovider,
        "request": request,
    }
    return templates.TemplateResponse(
        request=request,
        name="cloudproviders/card.html",
        context=context,
        status_code=status.HTTP_201_CREATED,
        headers={"HX-Trigger": "closeModal"},
    )


@html_router.delete(
    path="/cloudproviders/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=HTMLResponse,
)
def hx_delete_cloudprovider(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Delete a cloudprovider"""
    try:
        cloudprovider = delete_cloudprovider(
            id=id,
            request=request,
            db=db,
            current_user=current_user,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            cloudprovider = None
        else:
            raise e

    context = {
        "current_user": current_user,
        "cloudprovider": cloudprovider,
        "request": request,
    }
    return templates.TemplateResponse(
        request=request,
        name="shared/none.html",
        context=context,
        headers={"HX-Trigger": "closeModal"},
    )


@html_router.put(
    path="/cloudproviders/{id}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_update_cloudprovider(
    request: Request,
    id: int,
    updated_cloudprovider: schemas.CloudProviderUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Update a cloudprovider."""

    print(updated_cloudprovider.model_dump())
    try:
        cloudprovider = update_cloudprovider(
            id=id,
            updated_cloudprovider=updated_cloudprovider,
            request=request,
            db=db,
            current_user=current_user,
        )
    except HTTPException as e:
        print(e)  # TODO: replace with logger
        context = {
            "current_user": current_user,
            "message": "An error occurred while updating the cloudprovider. Please try again.",
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
        "cloudprovider": cloudprovider,
        "request": request,
    }
    return templates.TemplateResponse(
        request=request,
        name="cloudproviders/crud.html",
        context=context,
    )


######## Validation Route ########


def hx_validate_cloudprovider_name(
    cloudprovider: schemas.CloudProviderValidate,
    db: Session = Depends(get_db),
):
    if cloudprovider.name and len(cloudprovider.name) >= 3:
        return True
    return False


def hx_validate_cloudprovider_code(
    cloudprovider: schemas.CloudProviderValidate,
    db: Session = Depends(get_db),
):
    if cloudprovider.code and len(cloudprovider.code) >= 3:
        return True
    return False


@html_router.post(
    "/cloudproviders/validate/{field}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def hx_validate_cloudprovider_create_form(
    cloudprovider: schemas.CloudProviderValidate,
    field: str,
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    name_is_valid = hx_validate_cloudprovider_name(
        cloudprovider,
        db,
    )

    code_is_valid = hx_validate_cloudprovider_code(
        cloudprovider,
        db,
    )

    enable_submit_btn = name_is_valid and code_is_valid

    if field == "name":
        context = {
            "field": "name",
            "is_validated": name_is_valid,
            "value": cloudprovider.name,
            "ready_to_submit": enable_submit_btn,
        }
    elif field == "code":
        context = {
            "field": "code",
            "is_validated": code_is_valid,
            "value": cloudprovider.code,
            "ready_to_submit": enable_submit_btn,
        }

    response = templates.TemplateResponse(
        request=request,
        name="cloudproviders/validate.html",
        context=context,
    )

    return response
