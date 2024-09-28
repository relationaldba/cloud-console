import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db

json_router = APIRouter()


@json_router.get("/db", status_code=status.HTTP_200_OK)
async def database_health(db: sa.orm.Session = Depends(get_db)):
    """Checks the health of the database"""

    try:
        db.execute(statement=sa.text("SELECT 1"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e

    return {"status": "healthy", "message": "ok"}


@json_router.get("/app", status_code=status.HTTP_200_OK)
async def application_health(db: sa.orm.Session = Depends(get_db)):
    """Checks the health of the app"""

    try:
        db.execute(statement=sa.text("SELECT 1"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        ) from e

    return {"status": "healthy", "message": "ok"}
