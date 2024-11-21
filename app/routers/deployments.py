import re
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, true
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user, hx_get_current_user
from app.aws_stacks import aws_ec2standalone
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
    limit: int = 10,
    skip: int = 0,
    search: str | None = "",
    deleted: bool = False,
    cloudprovider_id: int | None = None,
):
    """Get all deployments in ascending order of created_at"""

    deployments = db.scalars(
        select(models.Deployment)
        .where(models.Deployment.name.contains(search) if search else true())
        .where(
            models.Deployment.deleted_at.isnot(None)
            if deleted
            else models.Deployment.deleted_at.is_(None)
        )
        .where(
            models.Deployment.cloudprovider_id == cloudprovider_id
            if cloudprovider_id
            else true()
        )
        .order_by(models.Deployment.created_at.desc())
        .limit(limit=limit)
        .offset(skip)
    ).all()

    if not deployments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "DEPLOYMENT_NOT_FOUND",
                "module": "deployments",
                "message": "The requested deployment(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

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
                "error_code": "DEPLOYMENT_NOT_FOUND",
                "module": "deployments",
                "message": "The requested deployment(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    return deployment


@json_router.post(
    path="/deployments",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=schemas.DeploymentResponse,
)
def create_deployment(
    new_deployment: schemas.DeploymentCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a deployment"""

    # Check if the deployment already exists, if yes, then raise an error
    deployment = db.scalar(
        select(models.Deployment).where(
            models.Deployment.name == new_deployment.name.upper()
        )
    )

    # Verify the deployment does not already exist
    if deployment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": "DEPLOYMENT_EXISTS",
                "module": "deployments",
                "message": "The deployment(s) you are trying to add already exist. Verify the details and try again.",
                "path": request.url.path,
            },
        )

    # Verify the environment exists
    environment = db.scalar(
        select(models.Environment).where(
            models.Environment.id == new_deployment.environment_id
        )
    )
    if not environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "ENVIRONMENT_NOT_FOUND",
                "module": "deployments",
                "message": "The requested environment(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    # Verify the stack exists
    stack = db.scalar(
        select(models.Stack).where(models.Stack.id == new_deployment.stack_id)
    )
    if not stack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "STACK_NOT_FOUND",
                "module": "deployments",
                "message": "The requested stack(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    # Verify the product exists
    product = db.scalar(
        select(models.Product).where(models.Product.id == new_deployment.product_id)
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "PRODUCT_NOT_FOUND",
                "module": "deployments",
                "message": "The requested product(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    # Store the stack and product properties in a separate variable
    # then remove the properties from the new_deployment object
    # the stack and product properties will be added after the deployment is created
    stack_properties = new_deployment.stack_properties or []
    # delattr(new_deployment, "stack_properties")
    product_properties = new_deployment.product_properties or []
    # delattr(new_deployment, "product_properties")
    deployment = models.Deployment(
        **new_deployment.model_dump(exclude={"stack_properties", "product_properties"}),
        created_by=current_user.id,
    )

    # Add the deployment to the database
    db.add(deployment)
    db.flush()
    db.refresh(instance=deployment)

    if stack_properties:
        for stack_property in stack_properties:
            property = models.StackProperty(
                **stack_property.model_dump(),
                stack_id=deployment.stack_id,
                deployment_id=deployment.id,
            )
            db.add(property)

    if product_properties:
        for product_property in product_properties:
            property = models.ProductProperty(
                **product_property.model_dump(),
                product_id=deployment.product_id,
                deployment_id=deployment.id,
            )
            db.add(property)

    db.commit()

    # Add code to create a FastAPI background task to synthesize and deploy the stack
    if stack.class_name == "AWSEc2Standalone":
        background_tasks.add_task(
            aws_ec2standalone.synth_and_deploy,
            deployment_id=deployment.id,
            deployment_name=deployment.name,
            vpc_cidr="10.24.1.0/24",
            db=db,
        )
    # TODO: Add code to dynamically assign an unused VPC CIDR to the deployment

    return deployment


@json_router.delete(
    path="/deployments/{id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=schemas.DeploymentResponse,
)
def delete_deployment(
    id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a deployment"""

    deployment = db.scalar(select(models.Deployment).where(models.Deployment.id == id))

    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "DEPLOYMENT_NOT_FOUND",
                "module": "deployments",
                "message": "The requested deployment(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    # Verify the stack exists
    stack = db.scalar(
        select(models.Stack).where(models.Stack.id == deployment.stack_id)
    )
    if not stack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "STACK_NOT_FOUND",
                "module": "deployments",
                "message": "The requested stack(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    deployment.status = models.DeploymentStatusEnum.DELETING
    db.commit()

    if stack.class_name == "AWSEc2Standalone":
        background_tasks.add_task(
            aws_ec2standalone.destroy_stack,
            deployment_id=deployment.id,
            deployment_name=deployment.name,
            db=db,
        )

    return deployment


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
                "error_code": "DEPLOYMENT_NOT_FOUND",
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

        for deployment in deployments:
            deployment.environment = db.scalar(
                select(models.Environment).where(
                    models.Environment.id == deployment.environment_id
                )
            )
            deployment.cloudprovider = db.scalar(
                select(models.CloudProvider).where(
                    models.CloudProvider.id == deployment.environment.cloudprovider_id
                )
            )
            deployment.stack = db.scalar(
                select(models.Stack).where(models.Stack.id == deployment.stack_id)
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
    cloudproviders = db.scalars(
        select(models.CloudProvider).where(models.CloudProvider.active)
    ).all()
    environments = db.scalars(
        select(models.Environment).where(models.Environment.active)
    ).all()
    stacks = db.scalars(select(models.Stack).where(models.Stack.active)).all()
    products = db.scalars(select(models.Product).where(models.Product.active)).all()

    context = {
        "current_user": current_user,
        "action": "create",
        "cloudproviders": cloudproviders,
        "environments": environments,
        "stacks": stacks,
        "products": products,
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
        deployment.environment = db.scalar(
            select(models.Environment).where(
                models.Environment.id == deployment.environment_id
            )
        )
        deployment.cloudprovider = db.scalar(
            select(models.CloudProvider).where(
                models.CloudProvider.id == deployment.environment.cloudprovider_id
            )
        )
        deployment.stack = db.scalar(
            select(models.Stack).where(models.Stack.id == deployment.stack_id)
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
        deployment.environment = db.scalar(
            select(models.Environment).where(
                models.Environment.id == deployment.environment_id
            )
        )
        deployment.cloudprovider = db.scalar(
            select(models.CloudProvider).where(
                models.CloudProvider.id == deployment.environment.cloudprovider_id
            )
        )
        deployment.stack = db.scalar(
            select(models.Stack).where(models.Stack.id == deployment.stack_id)
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
    background_tasks: BackgroundTasks,
    new_deployment: schemas.DeploymentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Create a deployment"""
    try:
        deployment = create_deployment(
            new_deployment=new_deployment,
            request=request,
            background_tasks=background_tasks,
            db=db,
            current_user=current_user,
        )
        deployment.environment = db.scalar(
            select(models.Environment).where(
                models.Environment.id == deployment.environment_id
            )
        )
        deployment.cloudprovider = db.scalar(
            select(models.CloudProvider).where(
                models.CloudProvider.id == deployment.environment.cloudprovider_id
            )
        )
        deployment.stack = db.scalar(
            select(models.Stack).where(models.Stack.id == deployment.stack_id)
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
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Delete a deployment"""
    try:
        deployment = delete_deployment(
            id=id,
            request=request,
            background_tasks=background_tasks,
            db=db,
            current_user=current_user,
        )
        deployment.environment = db.scalar(
            select(models.Environment).where(
                models.Environment.id == deployment.environment_id
            )
        )
        deployment.cloudprovider = db.scalar(
            select(models.CloudProvider).where(
                models.CloudProvider.id == deployment.environment.cloudprovider_id
            )
        )
        deployment.stack = db.scalar(
            select(models.Stack).where(models.Stack.id == deployment.stack_id)
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

    regex = re.compile(r"^[A-Za-z0-9-_]+$")
    name_is_valid = regex.match(deployment.name)  # type: ignore

    if (
        deployment.name
        and name_is_valid
        and len(deployment.name) >= 3
        and not deployment_exists
    ):
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

    response = templates.TemplateResponse(
        request=request,
        name="deployments/validate.html",
        context=context,
    )

    return response
