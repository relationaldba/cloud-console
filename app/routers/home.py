from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import hx_get_current_user
from app.config import config
from app.database import get_db

html_router = APIRouter()
json_router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


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
    "/",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def home(
    request: Request,
    current_user=Depends(hx_get_current_user),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    context = {"current_user": current_user, "config": config}

    response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context,
        headers={"Hx-Refresh": "true"},
    )

    return response
