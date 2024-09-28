from fastapi import APIRouter

from app.routers import (
    deployments,
    health,
    home,
    login,
    logout,
    products,
    services,
    stacks,
    users,
    validations
)

"""
    /*
     *
     *
     *      JSON Data API Routes
     *
     *
     */
"""
json_router = APIRouter()

json_router.include_router(
    products.json_router,
    prefix="/api",
    tags=["products"],
)
json_router.include_router(
    services.json_router,
    prefix="/api",
    tags=["services"],
)
json_router.include_router(
    stacks.json_router,
    prefix="/api",
    tags=["stacks"],
)
json_router.include_router(
    deployments.json_router,
    prefix="/api",
    tags=["deployments"],
)
json_router.include_router(
    users.json_router,
    prefix="/api",
    tags=["users"],
)
json_router.include_router(
    health.json_router,
    prefix="/api",
    tags=["health"],
)
json_router.include_router(
    login.json_router,
    prefix="/api",
    tags=["authentication"],
)


"""
    /*
     *
     *
     *      Hypermedia (HTML) API Routes
     *
     *
     */
"""
html_router = APIRouter()


html_router.include_router(
    products.html_router,
    tags=["products"],
)
html_router.include_router(
    services.html_router,
    tags=["services"],
)
html_router.include_router(
    stacks.html_router,
    tags=["stacks"],
)
html_router.include_router(
    deployments.html_router,
    tags=["deployments"],
)
html_router.include_router(
    login.html_router,
    tags=["authentication"],
)
html_router.include_router(
    logout.html_router,
    tags=["authentication"],
)
html_router.include_router(
    home.html_router,
    tags=["home"],
)
html_router.include_router(
    validations.html_router,
    tags=["modals"],
)