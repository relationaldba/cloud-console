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
    "/deployments",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.DeploymentResponse],
)
def get_all_deployments(
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: str | None = "",
):
    """Get all deployments in ascending order of name"""

    deployments = db.scalars(
        select(models.Deployment)
        .where(models.Deployment.name.contains(search))
        .order_by(models.Deployment.name)
        .limit(limit=limit)
        .offset(skip)
    ).all()

    if not deployments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="item not found",
        )

    return deployments


@json_router.get(
    "/deployments/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.DeploymentResponse,
)
def get_deployment(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    """Get a deployment by id"""

    deployment = db.scalar(select(models.Deployment).where(models.Deployment.id == id))

    if deployment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="item not found",
        )

    return deployment


@json_router.post(
    path="/deployments",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.DeploymentResponse,
)
def create_deployment(
    new_deployment: schemas.DeploymentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    """Create a deployment"""

    # Check if the deployment already exists, if yes, then raise an error
    deployment = db.scalar(
        select(models.Deployment)
        .where(models.Deployment.name == new_deployment.name)
        .limit(1)
    )

    if deployment is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="item already exists",
        )

    # deployment = models.Deployment(user_id=current_user.id, **new_deployment.model_dump())
    deployment = models.Deployment(**new_deployment.model_dump())

    # p.user_id = current_user.id
    db.add(deployment)
    db.commit()
    db.refresh(instance=deployment)
    return deployment


@json_router.delete(
    path="/deployments/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_deployment(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    """Delete a deployment"""

    deployment = db.scalar(select(models.Deployment).where(models.Deployment.id == id))

    if deployment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="item not found",
        )

    # elif deployment.user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="not authorized to perform requested action",
    #     )

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
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    """Update a deployment."""
    deployment = db.scalar(select(models.Deployment).where(models.Deployment.id == id))

    if deployment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="item not found",
        )
    # elif deployment.user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="not authorized to perform requested action",
    #     )

    # deployment.name = updated_deployment.name
    # deployment.active = updated_deployment.active

    deployment = models.Deployment(**updated_deployment.model_dump())

    db.add(deployment)
    db.commit()
    db.refresh(instance=deployment)
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
    current_user=Depends(auth.hx_get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: str | None = "",
):
    deployment_context = get_all_deployments(db=db, limit=limit, skip=skip, search=search)

    return templates.TemplateResponse(
        request=request, name="deployments.html", context={"deployments": deployment_context}
    )


@html_router.get(
    "/deployments/{id}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_get_deployment(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Get a deployment by id"""

    deployment_context = get_deployment(db=db, id=id)
    return templates.TemplateResponse(
        request=request, name="deployments.html", context={"deployments": [deployment_context]}
    )


@html_router.post(
    path="/deployments",
    status_code=status.HTTP_201_CREATED,
    response_class=HTMLResponse,
)
def hx_create_deployment(
    request: Request,
    new_deployment: schemas.DeploymentCreate,
    db: Session = Depends(get_db),
    # current_user=Depends(auth.get_current_user),
):
    """Create a deployment"""

    deployment_context = create_deployment(new_deployment=new_deployment, db=db)
    return templates.TemplateResponse(
        request=request, name="deployments.html", context={"deployments": [deployment_context]}
    )


@html_router.delete(
    path="/deployments/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=HTMLResponse,
)
def hx_delete_deployment(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    """Delete a deployment"""

    # query = db.query(models.Deployment).filter(models.Deployment.id == id)
    deployment = db.scalar(select(models.Deployment).where(models.Deployment.id == id))

    if deployment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="deployment not found",
        )

    # elif deployment.user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="not authorized to perform requested action",
    #     )

    db.delete(deployment)
    db.commit()


@html_router.put(
    path="/deployments/{id}",
    status_code=status.HTTP_201_CREATED,
    response_class=HTMLResponse,
)
def hx_update_deployment(
    id: int,
    updated_deployment: schemas.DeploymentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    """Update a deployment."""
    deployment = db.scalar(select(models.Deployment).where(models.Deployment.id == id))

    if deployment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="deployment not found"
        )
    # elif deployment.user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="not authorized to perform requested action",
    #     )

    # deployment.name = updated_deployment.name
    # deployment.active = updated_deployment.active

    deployment = models.Deployment(**updated_deployment.model_dump())

    # db.add(deployment)
    db.commit()
    db.refresh(instance=deployment)
    # deployment.votes = 0
    return deployment
