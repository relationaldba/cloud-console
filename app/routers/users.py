from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import orm

from app import auth, models, schemas
from app.database import get_db

json_router = APIRouter()


@json_router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserResponse,
)
def create_user(user: schemas.UserCreate, db: orm.Session = Depends(get_db)):
    """Create a User"""

    query = db.query(models.User).filter(models.User.email == user.email)

    if query.first() is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="email exists",
        )

    # Encrypt the password
    hashed_password = auth.hash_password(user.password)
    user.password = hashed_password

    new_user = models.User(**user.model_dump())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@json_router.get(
    path="/users/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserResponse,
)
def get_user(id: int, db: orm.Session = Depends(get_db)):
    """Get a User"""

    user = db.query(models.User).filter(models.User.id == id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"user id: {id} not found"
        )

    return user
