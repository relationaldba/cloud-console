from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse

html_router = APIRouter()


"""
    /*
     *
     *
     *      Hypermedia (HTML) API Routes
     *
     *
     */
"""


@html_router.get(
    path="/logout",
    # status_code=status.HTTP_303_SEE_OTHER,
    response_class=RedirectResponse,
)
def hx_logout(response: RedirectResponse) -> RedirectResponse:
    """Logout the user."""

    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response
