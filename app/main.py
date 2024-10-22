from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

# from app.auth import NotAuthenticatedException
from app.database import Base, engine
from app.exceptions.exceptions import InvalidCredentialsException
from app.routers import html_router, json_router

# Create Metadata
Base.metadata.create_all(bind=engine)


app = FastAPI()
app.include_router(json_router)
app.include_router(html_router)
app.mount(
    path="/static",
    app=StaticFiles(directory="app/static"),
    name="static",
)

templates = Jinja2Templates(directory="app/templates", auto_reload=True)


origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(InvalidCredentialsException)
async def hx_authentixation_(request: Request, exc: InvalidCredentialsException):
    """

    Redirect the user to the login page if authentication fails or if the user does not have the necessary permissions

    Parameters
    ----------
    request : fastapi.Request
        The request that triggered this exception
    exc : fastapi.HTTPException
        The exception that was raised

    Returns
    -------
    fastapi.Response
        A 303 redirect response that redirects the user to the login page if authentication fails
    """
    print("InvalidCredentialsException, redirecting to login page")
    response = RedirectResponse(
        url="/login",
        status_code=status.HTTP_303_SEE_OTHER,
        headers={"HX-Refresh": "true"},
    )
    response.delete_cookie("auth_token")
    return response


# @app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """ """
    print("http exception handler")
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        context = {"user": None}
        response = RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"HX-Refresh": "true"},
        )
        response.delete_cookie("auth_token")
        return response

    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        context = {
            "request": request,
            "exception": exc,
            "message": "You do not have permission to access this resource.",
        }
        # response = templates.TemplateResponse(
        #     request=request,
        #     name="error/error-message.html",
        #     context=context,
        # )
        # return response

    elif exc.status_code == status.HTTP_404_NOT_FOUND:
        context = {
            "request": request,
            "exception": exc,
            "message": "The requested resource could not be found.",
        }
        # response = templates.TemplateResponse(
        #     request=request,
        #     name="error/error-message.html",
        #     context=context,
        # )
        # return response

    elif exc.status_code == status.HTTP_409_CONFLICT:
        context = {
            "request": request,
            "exception": exc,
            "message": "There was a conflict while processing your request.",
        }
        # response = templates.TemplateResponse(
        #     request=request,
        #     name="error/error-message.html",
        #     context=context,
        # )
        # return response

    # elif exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
    #     context = {
    #         "request": request,
    #         "exception": exc,
    #         "message": "Please check the data you entered.",
    #     }
    # response = templates.TemplateResponse(
    #     request=request,
    #     name="error/error-message.html",
    #     context=context,
    # )
    # return response

    elif exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        context = {
            "request": request,
            "exception": exc,
            "message": "An unknown error occurred. Please try again later.",
        }
        # response = templates.TemplateResponse(
        #     request=request,
        #     name="error/error-message.html",
        #     context=context,
        # )
        # return response
    #     context = {"request": request, "exception": exc}
    #     response = templates.TemplateResponse(
    #         request=request,
    #         name="error/error-message.html",
    #         context=context,
    #     )
    #     return response

    # return exc
    response = templates.TemplateResponse(
        request=request,
        name="errors/error-message.html",
        context=context,
    )
    return response

"""
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print("validation exception handler")
    print(exc.errors()[0])
    # if exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
    context = {
        "request": request,
        "exception": exc,
        "message": f"{exc.errors()[0].get('msg')}. Please check the data you entered.",
    }
    response = templates.TemplateResponse(
        request=request,
        name="errors/error-message.html",
        context=context,
        headers={"HX-Reswap": "none"},
    )
    return response
"""