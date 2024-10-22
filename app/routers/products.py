from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, HttpUrl, ValidationError
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


################################################################################
#
#
#
#                           JSON Data API Routes
#
#
#
################################################################################


@json_router.get(
    "/products",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.ProductResponse],
)
def get_all_products(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    limit: int = 50,
    skip: int = 0,
    search: str | None = "",
):
    """Get all products in ascending order of name"""

    products = db.scalars(
        select(models.Product)
        .where(models.Product.name.contains(search))
        # .where(models.Product.active)
        .order_by(models.Product.name)
        .limit(limit=limit)
        .offset(skip)
    ).all()

    if products is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "PRODUCT_NOT_FOUND",
                "module": "Products",
                "message": "The requested Product(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    return products


@json_router.get(
    "/products/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ProductResponse,
)
def get_product(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a product by id"""

    product = db.scalar(select(models.Product).where(models.Product.id == id))

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "PRODUCT_NOT_FOUND",
                "module": "Products",
                "message": "The requested Product(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    return product


@json_router.post(
    path="/products",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ProductResponse,
)
def create_product(
    new_product: schemas.ProductCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a product"""
    new_product.created_by = current_user.id

    # Check if the product already exists, if yes, then raise an error
    product = db.scalar(
        select(models.Product)
        .where(models.Product.name == new_product.name)
        .where(models.Product.version == new_product.version),
    )

    if product:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": "PRODUCT_EXISTS",
                "module": "Products",
                "message": "The product(s) you are trying to add already exist. Verify the details and try again.",
                "path": request.url.path,
            },
        )

    product = models.Product(**new_product.model_dump())
    db.add(product)
    db.commit()
    db.refresh(instance=product)
    return product


@json_router.delete(
    path="/products/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a product"""

    product = db.scalar(select(models.Product).where(models.Product.id == id))

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "PRODUCT_NOT_FOUND",
                "module": "Products",
                "message": "The requested Product(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    db.delete(product)
    db.commit()


@json_router.put(
    path="/products/{id}",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ProductResponse,
)
def update_product(
    id: int,
    updated_product: schemas.ProductUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a product."""
    product = db.scalar(select(models.Product).where(models.Product.id == id))

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "PRODUCT_NOT_FOUND",
                "module": "Products",
                "message": "The requested Product(s) could not be found, or you do not have permission to access them.",
                "path": request.url.path,
            },
        )

    for key, value in updated_product.model_dump(
        exclude_unset=False, exclude_none=True
    ).items():
        setattr(product, key, value)

    db.commit()
    db.refresh(instance=product)
    return product


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
    "/products",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def hx_get_all_products(
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    skip: int = 0,
    search: str | None = "",
):
    try:
        products = get_all_products(
            limit=limit,
            skip=skip,
            search=search,
            request=request,
            current_user=current_user,
            db=db,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            products = []
        else:
            raise e

    context = {
        "current_user": current_user,
        "products": products,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="products/index.html",
        context=context,
    )

    return response


@html_router.get(
    "/products/create",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_product_create_form(
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    """Get a product by id"""

    context = {
        "current_user": current_user,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="products/create.html",
        context=context,
    )

    return response


# @html_router.get(
#     "/products/{id}/edit",
#     status_code=status.HTTP_200_OK,
#     response_class=HTMLResponse,
# )
# def hx_edit_product(
#     id: int,
#     request: Request,
#     current_user=Depends(hx_get_current_user),
#     db: Session = Depends(get_db),
# ):
#     """Get a product by id"""

#     try:
#         product = get_product(
#             request=request,
#             db=db,
#             id=id,
#         )
#     except HTTPException as e:
#         if e.status_code == status.HTTP_404_NOT_FOUND:
#             product = None
#         else:
#             raise e

#     context = {
#         "current_user": current_user,
#         "product": product,
#         "request": request,
#     }

#     response = templates.TemplateResponse(
#         request=request,
#         name="products/edit.html",
#         context=context,
#     )

#     return response


@html_router.get(
    "/products/{id}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_get_product(
    id: int,
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    """Get a product by id"""

    try:
        product = get_product(
            request=request,
            db=db,
            id=id,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            product = None
        else:
            raise e

    context = {
        "current_user": current_user,
        "product": product,
        "request": request,
    }

    response = templates.TemplateResponse(
        request=request,
        name="products/detail.html",
        context=context,
    )
    return response


@html_router.post(
    path="/products",
    status_code=status.HTTP_201_CREATED,
    response_class=HTMLResponse,
)
def hx_create_product(
    request: Request,
    new_product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Create a product"""
    try:
        product = create_product(
            new_product=new_product,
            request=request,
            db=db,
            current_user=current_user,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            product = None
        else:
            raise e

    context = {
        "current_user": current_user,
        "product": product,
        "request": request,
    }
    return templates.TemplateResponse(
        request=request,
        name="products/card.html",
        context=context,
        status_code=status.HTTP_201_CREATED,
        headers={"HX-Trigger": "closeModal"},
    )


@html_router.delete(
    path="/products/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=HTMLResponse,
)
def hx_delete_product(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Delete a product"""
    try:
        product = delete_product(
            id=id,
            request=request,
            db=db,
            current_user=current_user,
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            product = None
        else:
            raise e

    context = {
        "current_user": current_user,
        "product": product,
        "request": request,
    }
    return templates.TemplateResponse(
        request=request,
        name="products/delete.html",
        context=context,
        headers={"HX-Trigger": "closeModal"},
    )


@html_router.put(
    path="/products/{id}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def hx_update_product(
    request: Request,
    id: int,
    updated_product: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(hx_get_current_user),
):
    """Update a product."""

    print(updated_product.model_dump())
    try:
        product = update_product(
            id=id,
            updated_product=updated_product,
            request=request,
            db=db,
            current_user=current_user,
        )
    except HTTPException as e:
        print(e)  # TODO: replace with logger
        context = {
            "current_user": current_user,
            "message": "An error occurred while updating the product. Please try again.",
            "request": request,
        }
        return templates.TemplateResponse(
            request=request,
            name="shared/error-message.html",
            headers={"HX-Reswap": "none"},
        )

    context = {
        "current_user": current_user,
        "product": product,
        "request": request,
    }
    return templates.TemplateResponse(
        request=request,
        name="products/detail.html",
        context=context,
    )


######## Validation Route ########


def hx_validate_product_name(
    product: schemas.ProductValidate,
    db: Session = Depends(get_db),
):
    if product.name and len(product.name) >= 3:
        return True
    return False


def hx_validate_product_version(
    product: schemas.ProductValidate,
    db: Session = Depends(get_db),
):
    version_exists = db.scalars(
        select(models.Product).where(models.Product.version == product.version)
    ).first()

    if product.version and not version_exists and len(product.version) >= 3:
        return True
    return False


def hx_validate_product_repository_url(
    product: schemas.ProductValidate,
    db: Session = Depends(get_db),
):
    class ValidateUrl(BaseModel):
        url: HttpUrl

    if product.repository_url and len(product.repository_url) >= 3:
        try:
            ValidateUrl(url=product.repository_url)  # type: ignore
            return True

        except ValidationError:
            return False

    return False


def hx_validate_product_repository_username(
    product: schemas.ProductValidate,
    db: Session = Depends(get_db),
):
    if product.repository_username and len(product.repository_username) >= 3:
        return True
    return False


@html_router.post(
    "/products/validate/{field}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def hx_validate_product_create_form(
    product: schemas.ProductValidate,
    field: str,
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    name_is_valid = hx_validate_product_name(
        product,
        db,
    )
    version_is_valid = hx_validate_product_version(
        product,
        db,
    )
    repository_url_is_valid = hx_validate_product_repository_url(
        product,
        db,
    )
    repository_username_is_valid = hx_validate_product_repository_username(
        product,
        db,
    )

    enable_submit_btn = (
        name_is_valid
        and version_is_valid
        and repository_url_is_valid
        and repository_username_is_valid
    )

    if field == "name":
        context = {
            "field": "name",
            "is_validated": name_is_valid,
            "value": product.name,
            "ready_to_submit": enable_submit_btn,
        }
    elif field == "version":
        context = {
            "field": "version",
            "is_validated": version_is_valid,
            "value": product.version,
            "ready_to_submit": enable_submit_btn,
        }
    elif field == "repository_url":
        context = {
            "field": "repository_url",
            "is_validated": repository_url_is_valid,
            "value": product.repository_url,
            "ready_to_submit": enable_submit_btn,
        }
    elif field == "repository_username":
        context = {
            "field": "repository_username",
            "is_validated": repository_username_is_valid,
            "value": product.repository_username,
            "ready_to_submit": enable_submit_btn,
        }

    response = templates.TemplateResponse(
        request=request,
        name="products/validate-create.html",
        context=context,
    )

    return response


@html_router.post(
    "/products/validate/{field}/update",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def hx_validate_product_update_form(
    product: schemas.ProductValidate,
    field: str,
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    name_is_valid = hx_validate_product_name(
        product,
        db,
    )
    version_is_valid = hx_validate_product_version(
        product,
        db,
    )
    repository_url_is_valid = hx_validate_product_repository_url(
        product,
        db,
    )
    repository_username_is_valid = hx_validate_product_repository_username(
        product,
        db,
    )

    if field == "name":
        context = {
            "field": "name",
            "is_validated": name_is_valid,
            "value": product.name,
        }
    elif field == "version":
        context = {
            "field": "version",
            "is_validated": version_is_valid,
            "value": product.version,
        }
    elif field == "repository_url":
        context = {
            "field": "repository_url",
            "is_validated": repository_url_is_valid,
            "value": product.repository_url,
        }
    elif field == "repository_username":
        context = {
            "field": "repository_username",
            "is_validated": repository_username_is_valid,
            "value": product.repository_username,
        }

    response = templates.TemplateResponse(
        request=request,
        name="products/validate-update.html",
        context=context,
    )

    return response
