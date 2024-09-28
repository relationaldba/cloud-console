from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import auth, models, schemas
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
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: str | None = "",
):
    """Get all stacks in ascending order of name"""

    stacks = db.scalars(
        select(models.Stack)
        .where(models.Stack.name.contains(search))
        .order_by(models.Stack.name)
        .limit(limit=limit)
        .offset(skip)
    ).all()

    if not stacks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="item not found",
        )

    return stacks


@json_router.get(
    "/stacks/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.StackResponse,
)
def get_stack(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    """Get a stack by id"""

    stack = db.scalar(select(models.Stack).where(models.Stack.id == id))

    if stack is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="item not found",
        )

    return stack


@json_router.post(
    path="/stacks",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.StackResponse,
)
def create_stack(
    new_stack: schemas.StackCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    """Create a stack"""

    # Check if the stack already exists, if yes, then raise an error
    stack = db.scalar(
        select(models.Stack)
        .where(models.Stack.name == new_stack.name)
        .limit(1)
    )

    if stack is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="item already exists",
        )

    # stack = models.Stack(user_id=current_user.id, **new_stack.model_dump())
    stack = models.Stack(**new_stack.model_dump())

    # p.user_id = current_user.id
    db.add(stack)
    db.commit()
    db.refresh(instance=stack)
    return stack


@json_router.delete(
    path="/stacks/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_stack(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    """Delete a stack"""

    stack = db.scalar(select(models.Stack).where(models.Stack.id == id))

    if stack is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="item not found",
        )

    # elif stack.user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="not authorized to perform requested action",
    #     )

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
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    """Update a stack."""
    stack = db.scalar(select(models.Stack).where(models.Stack.id == id))

    if stack is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="item not found",
        )
    # elif stack.user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="not authorized to perform requested action",
    #     )

    # stack.name = updated_stack.name
    # stack.active = updated_stack.active

    stack = models.Stack(**updated_stack.model_dump())

    db.add(stack)
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
    current_user=Depends(auth.hx_get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: str | None = "",
):
    stack_context = get_all_stacks(db=db, limit=limit, skip=skip, search=search)

    return templates.TemplateResponse(
        request=request, name="stacks.html", context={"stacks": stack_context}
    )


@html_router.get(
    "/stacks/{id}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_get_stack(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Get a stack by id"""

    stack_context = get_stack(db=db, id=id)
    return templates.TemplateResponse(
        request=request, name="stacks.html", context={"stacks": [stack_context]}
    )


@html_router.post(
    path="/stacks",
    status_code=status.HTTP_201_CREATED,
    response_class=HTMLResponse,
)
def hx_create_stack(
    request: Request,
    new_stack: schemas.StackCreate,
    db: Session = Depends(get_db),
    # current_user=Depends(auth.get_current_user),
):
    """Create a stack"""

    stack_context = create_stack(new_stack=new_stack, db=db)
    return templates.TemplateResponse(
        request=request, name="stacks.html", context={"stacks": [stack_context]}
    )


@html_router.delete(
    path="/stacks/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=HTMLResponse,
)
def hx_delete_stack(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    """Delete a stack"""

    # query = db.query(models.Stack).filter(models.Stack.id == id)
    stack = db.scalar(select(models.Stack).where(models.Stack.id == id))

    if stack is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="stack not found",
        )

    # elif stack.user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="not authorized to perform requested action",
    #     )

    db.delete(stack)
    db.commit()


@html_router.put(
    path="/stacks/{id}",
    status_code=status.HTTP_201_CREATED,
    response_class=HTMLResponse,
)
def hx_update_stack(
    id: int,
    updated_stack: schemas.StackUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    """Update a stack."""
    stack = db.scalar(select(models.Stack).where(models.Stack.id == id))

    if stack is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="stack not found"
        )
    # elif stack.user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="not authorized to perform requested action",
    #     )

    # stack.name = updated_stack.name
    # stack.active = updated_stack.active

    stack = models.Stack(**updated_stack.model_dump())

    # db.add(stack)
    db.commit()
    db.refresh(instance=stack)
    # stack.votes = 0
    return stack
