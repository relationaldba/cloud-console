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

    for stack in stacks:
        user = db.scalar(select(models.User).where(models.User.id == stack.created_by))
        if user:
            stack.creator = user.email

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

    user = db.scalar(select(models.User).where(models.User.id == stack.created_by))
    if user:
        stack.creator = user.email

    return stack


@json_router.post(
    path="/stacks",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.StackResponse,
)
def create_stack(
    new_stack: schemas.StackCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a stack"""

    # Check if the stack already exists, if yes, then raise an error
    stack = db.scalar(select(models.Stack).where(models.Stack.name == new_stack.name))

    if stack:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": "STACK_EXISTS",
                "module": "stacks",
                "message": "The stack(s) you are trying to add already exist. Verify the details and try again.",
                "path": request.url.path,
            },
        )

    stack = models.Stack(**new_stack.model_dump(), created_by=current_user.id)
    db.add(stack)
    db.commit()
    db.refresh(instance=stack)
    stack.creator = current_user.email
    return stack


@json_router.delete(
    path="/stacks/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_stack(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a stack"""

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

    db.delete(stack)
    db.commit()


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

    for key, value in updated_stack.model_dump(
        exclude_unset=False, exclude_none=True
    ).items():
        setattr(stack, key, value)

    db.commit()
    db.refresh(instance=stack)
    user = db.scalar(select(models.User).where(models.User.id == stack.created_by))
    if user:
        stack.creator = user.email
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
    "/stacks/create",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_stack_create_form(
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    """Get a stack by id"""

    cloudproviders = db.scalars(select(models.CloudProvider)).all()

    context = {
        "current_user": current_user,
        "action": "create",
        "cloudproviders": cloudproviders,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="stacks/crud.html",
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



@html_router.post(
    path="/stacks",
    status_code=status.HTTP_201_CREATED,
    response_class=HTMLResponse,
)
def hx_create_stack(
    request: Request,
    new_stack: schemas.StackCreate,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Create a stack"""
    try:
        stack = create_stack(
            new_stack=new_stack,
            request=request,
            db=db,
            current_user=current_user,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_409_CONFLICT:
            stack = None
        else:
            raise e

    context = {
        "current_user": current_user,
        "stack": stack,
        "request": request,
    }
    return templates.TemplateResponse(
        request=request,
        name="stacks/card.html",
        context=context,
        status_code=status.HTTP_201_CREATED,
        headers={"HX-Trigger": "closeModal"},
    )


@html_router.delete(
    path="/stacks/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=HTMLResponse,
)
def hx_delete_stack(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Delete a stack"""
    try:
        stack = delete_stack(
            id=id,
            request=request,
            db=db,
            current_user=current_user,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            stack = None
        else:
            raise e

    context = {
        "current_user": current_user,
        "stack": stack,
        "request": request,
    }
    return templates.TemplateResponse(
        request=request,
        name="shared/none.html",
        context=context,
        headers={"HX-Trigger": "closeModal"},
    )


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


######## Validation Route ########


def hx_validate_stack_name(
    stack: schemas.StackValidate,
    db: Session = Depends(get_db),
):
    stack_exists = db.scalars(
        select(models.Stack).where(models.Stack.name == stack.name)
    ).first()
    if stack.name and len(stack.name) >= 3 and not stack_exists:
        return True
    return False


def hx_validate_stack_class_name(
    stack: schemas.StackValidate,
    db: Session = Depends(get_db),
):
    if stack.class_name and len(stack.class_name) >= 3:
        return True
    return False


@html_router.post(
    "/stacks/validate/{field}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def hx_validate_stack_create_form(
    stack: schemas.StackValidate,
    field: str,
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    name_is_valid = hx_validate_stack_name(
        stack,
        db,
    )

    class_name_is_valid = hx_validate_stack_class_name(
        stack,
        db,
    )

    enable_submit_btn = name_is_valid and class_name_is_valid

    if field == "name":
        context = {
            "field": "name",
            "is_validated": name_is_valid,
            "value": stack.name,
            "ready_to_submit": enable_submit_btn,
        }

    elif field == "class_name":
        context = {
            "field": "class_name",
            "is_validated": class_name_is_valid,
            "value": stack.class_name,
            "ready_to_submit": enable_submit_btn,
        }

    response = templates.TemplateResponse(
        request=request,
        name="stacks/validate.html",
        context=context,
    )

    return response
