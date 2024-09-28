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
    "/services",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.ServiceResponse],
)
def get_all_services(
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: str | None = "",
):
    """Get all services in ascending order of name"""

    services = db.scalars(
        select(models.Service)
        .where(models.Service.name.contains(search))
        .order_by(models.Service.name)
        .limit(limit=limit)
        .offset(skip)
    ).all()

    if not services:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="item not found",
        )

    return services


@json_router.get(
    "/services/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ServiceResponse,
)
def get_service(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    """Get a service by id"""

    service = db.scalar(select(models.Service).where(models.Service.id == id))

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="item not found",
        )

    return service


@json_router.post(
    path="/services",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ServiceResponse,
)
def create_service(
    new_service: schemas.ServiceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    """Create a service"""

    # Check if the service already exists, if yes, then raise an error
    service = db.scalar(
        select(models.Service)
        .where(models.Service.name == new_service.name)
        .limit(1)
    )

    if service is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="item already exists",
        )

    # service = models.Service(user_id=current_user.id, **new_service.model_dump())
    service = models.Service(**new_service.model_dump())

    # p.user_id = current_user.id
    db.add(service)
    db.commit()
    db.refresh(instance=service)
    return service


@json_router.delete(
    path="/services/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_service(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    """Delete a service"""

    service = db.scalar(select(models.Service).where(models.Service.id == id))

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="item not found",
        )

    # elif service.user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="not authorized to perform requested action",
    #     )

    db.delete(service)
    db.commit()


@json_router.put(
    path="/services/{id}",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ServiceResponse,
)
def update_service(
    id: int,
    updated_service: schemas.ServiceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    """Update a service."""
    service = db.scalar(select(models.Service).where(models.Service.id == id))

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="item not found",
        )
    # elif service.user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="not authorized to perform requested action",
    #     )

    # service.name = updated_service.name
    # service.active = updated_service.active

    service = models.Service(**updated_service.model_dump())

    db.add(service)
    db.commit()
    db.refresh(instance=service)
    return service


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
    "/services",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def hx_get_all_services(
    request: Request,
    current_user=Depends(auth.hx_get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: str | None = "",
):
    service_context = get_all_services(db=db, limit=limit, skip=skip, search=search)

    return templates.TemplateResponse(
        request=request, name="services.html", context={"services": service_context}
    )


@html_router.get(
    "/services/{id}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_get_service(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Get a service by id"""

    service_context = get_service(db=db, id=id)
    return templates.TemplateResponse(
        request=request, name="services.html", context={"services": [service_context]}
    )


@html_router.post(
    path="/services",
    status_code=status.HTTP_201_CREATED,
    response_class=HTMLResponse,
)
def hx_create_service(
    request: Request,
    new_service: schemas.ServiceCreate,
    db: Session = Depends(get_db),
    # current_user=Depends(auth.get_current_user),
):
    """Create a service"""

    service_context = create_service(new_service=new_service, db=db)
    return templates.TemplateResponse(
        request=request, name="services.html", context={"services": [service_context]}
    )


@html_router.delete(
    path="/services/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=HTMLResponse,
)
def hx_delete_service(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    """Delete a service"""

    # query = db.query(models.Service).filter(models.Service.id == id)
    service = db.scalar(select(models.Service).where(models.Service.id == id))

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="service not found",
        )

    # elif service.user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="not authorized to perform requested action",
    #     )

    db.delete(service)
    db.commit()


@html_router.put(
    path="/services/{id}",
    status_code=status.HTTP_201_CREATED,
    response_class=HTMLResponse,
)
def hx_update_service(
    id: int,
    updated_service: schemas.ServiceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    """Update a service."""
    service = db.scalar(select(models.Service).where(models.Service.id == id))

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="service not found"
        )
    # elif service.user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="not authorized to perform requested action",
    #     )

    # service.name = updated_service.name
    # service.active = updated_service.active

    service = models.Service(**updated_service.model_dump())

    # db.add(service)
    db.commit()
    db.refresh(instance=service)
    # service.votes = 0
    return service
