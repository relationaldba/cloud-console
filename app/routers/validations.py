from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import hx_get_current_user
from app.database import get_db

html_router = APIRouter()
json_router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


# @html_router.get(
#     "/modals/close",
#     status_code=status.HTTP_200_OK,
#     response_class=HTMLResponse,
# )
# async def hx_close_modal(
#     request: Request,
#     current_user=Depends(hx_get_current_user),
#     db: Session = Depends(get_db),
# ):
#     response = templates.TemplateResponse(
#         request=request,
#         name="none.html",
#         headers={"HX-Trigger": "closeModal"},
#     )

#     return response


@html_router.get(
    "/validations/product",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def hx_validate_email(
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    response = templates.TemplateResponse(
        request=request,
        name="none.html",
    )

    return response



@html_router.get(
    "/validations/url",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def hx_validate_url(
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
):
    response = templates.TemplateResponse(
        request=request,
        name="none.html",
    )

    return response