from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# from .environments import EnvironmentResponse


class UserBase(BaseModel):
    """The base model for the User object"""

    model_config = ConfigDict(
        str_min_length=3,
        str_max_length=128,
        str_strip_whitespace=True,
    )

    first_name: str
    last_name: str
    email: EmailStr

    # class Config:
    #     """Pydantic config"""

    #     from_attributes = True  # orm_mode  in pydantic v1


class UserCreate(UserBase):
    """The model for creating the User object"""

    password: str


class UserUpdate(UserBase):
    """The model for updating the User object"""

    model_config = ConfigDict(
        str_min_length=3,
        str_max_length=128,
        str_strip_whitespace=True,
    )

    first_name: str
    last_name: str
    email: EmailStr 
    password: str | None = Field(default=None, min_length=0)
    active: bool = False


class UserLogin(BaseModel):
    """The model for logging in the User"""

    model_config = ConfigDict(
        str_min_length=1,
        str_max_length=256,
        str_strip_whitespace=True,
    )

    email: EmailStr
    password: str


class UserAuthenticated(BaseModel):
    """The model for logging in the User"""

    model_config = ConfigDict(
        str_min_length=1,
        str_max_length=256,
        str_strip_whitespace=True,
    )

    id: int
    email: EmailStr


class UserResponse(UserBase):
    """The model for reading the User object"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None = None


class UserValidate(BaseModel):
    """The base model for the User object"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    password: str | None = None