from fastapi import APIRouter

from app.routers import (
    cloudproviders,
    deployments,
    environments,
    health,
    home,
    login,
    logout,
    products,
    stacks,
    users,
    validations,
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
    environments.json_router,
    prefix="/api",
    tags=["environments"],
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
    cloudproviders.json_router,
    prefix="/api",
    tags=["cloudproviders"],
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
    include_in_schema=False,
)
html_router.include_router(
    environments.html_router,
    tags=["environments"],
    include_in_schema=False,
)
html_router.include_router(
    stacks.html_router,
    tags=["stacks"],
    include_in_schema=False,
)
html_router.include_router(
    deployments.html_router,
    tags=["deployments"],
    include_in_schema=False,
)
html_router.include_router(
    cloudproviders.html_router,
    tags=["cloudproviders"],
    include_in_schema=False,
)
html_router.include_router(
    login.html_router,
    tags=["authentication"],
    include_in_schema=False,
)
html_router.include_router(
    logout.html_router,
    tags=["authentication"],
    include_in_schema=False,
)
html_router.include_router(
    home.html_router,
    tags=["home"],
    include_in_schema=False,
)
html_router.include_router(
    users.html_router,
    tags=["users"],
    include_in_schema=False,
)
