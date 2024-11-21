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
    "/stacks",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.StackResponse],
)
def get_all_stacks(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    limit: int = 50,
    skip: int = 0,
    search: str | None = "",
    cloudprovider_id: int | None = None,
):
    """Get all stacks in ascending order of name"""

    stacks = db.scalars(
        select(models.Stack)
        .where(models.Stack.name.contains(search))
        # .where(models.Stack.active)
        .where(
            models.Stack.cloudprovider_id == cloudprovider_id
            if cloudprovider_id
            else models.Stack.cloudprovider_id != -1
        )
        .order_by(models.Stack.name)
        .limit(limit=limit)
        .offset(skip)
    ).all()

    if not stacks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "STACK_NOT_FOUND",
                "module": "stacks",
                "message": "The requested stack(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    return stacks


@json_router.get(
    "/stacks/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.StackResponse,
)
def get_stack(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a stack by id"""

    stack = db.scalar(select(models.Stack).where(models.Stack.id == id))

    if not stack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "STACK_NOT_FOUND",
                "module": "stacks",
                "message": "The requested stack(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    return stack


@json_router.put(
    path="/stacks/{id}",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.StackResponse,
)
def update_stack(
    id: int,
    updated_stack: schemas.StackUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a stack."""
    stack = db.scalar(select(models.Stack).where(models.Stack.id == id))

    if not stack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "STACK_NOT_FOUND",
                "module": "stacks",
                "message": "The requested stack(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    # for key, value in updated_stack.model_dump(
    #     exclude_unset=False, exclude_none=True
    # ).items():
    #     setattr(stack, key, value)

    if updated_stack.active:
        stack.active = True
    else:
        stack.active = False

    db.commit()
    db.refresh(instance=stack)
    return stack


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
    "/stacks",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def hx_get_all_stacks(
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    skip: int = 0,
    search: str | None = "",
    cloudprovider_id: int | None = None,
):
    try:
        stacks = get_all_stacks(
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
            stacks = []
        else:
            raise e

    context = {
        "current_user": current_user,
        "action": "read",
        "stacks": stacks,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="stacks/index.html",
        context=context,
    )

    return response


@html_router.get(
    "/stacks/{id}/edit",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_edit_stack(
    id: int,
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    """Get a stack by id"""

    try:
        stack = get_stack(
            request=request,
            db=db,
            id=id,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            stack = None
        else:
            raise e
        # TODO: Replace with logger

    context = {
        "current_user": current_user,
        "action": "update",
        "stack": stack,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="stacks/crud.html",
        context=context,
    )

    return response


@html_router.get(
    "/stacks/{id}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_get_stack(
    id: int,
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    """Get a stack by id"""

    try:
        stack = get_stack(
            request=request,
            db=db,
            id=id,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            stack = None
        else:
            raise e

    context = {
        "current_user": current_user,
        "action": "read",
        "stack": stack,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="stacks/crud.html",
        context=context,
    )
    return response


# This route is for Cascading select when creating a deployment
@html_router.get(
    "/stacks-cloudproviders",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def hx_get_stacks_by_cloudprovider_id(
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
    cloudprovider_id: int | None = None,
):
    try:
        stacks = get_all_stacks(
            cloudprovider_id=cloudprovider_id,
            request=request,
            current_user=current_user,
            db=db,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            stacks = []
        else:
            raise e

    context = {
        "current_user": current_user,
        "action": "create",
        "stacks": stacks,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="stacks/stacks-select.html",
        context=context,
    )

    return response




@html_router.put(
    path="/stacks/{id}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_update_stack(
    request: Request,
    id: int,
    updated_stack: schemas.StackUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Update a stack."""

    try:
        stack = update_stack(
            id=id,
            updated_stack=updated_stack,
            request=request,
            db=db,
            current_user=current_user,
        )
    except HTTPException as e:
        print(e)  # TODO: replace with logger
        context = {
            "current_user": current_user,
            "message": "An error occurred while updating the stack. Please try again.",
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
        "stack": stack,
        "request": request,
    }
    return templates.TemplateResponse(
        request=request,
        name="stacks/crud.html",
        context=context,
    )

