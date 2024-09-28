from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .users import UserResponse


class ProductBase(BaseModel):
    """The base model for the Product object"""

    model_config = ConfigDict(
        str_min_length=3,
        str_max_length=256,
        str_strip_whitespace=True,
    )

    name: str
    version: str = Field(
        max_length=16,
    )
    repository_url: str
    repository_username: str
    repository_password: str | None = Field(
        min_length=0,
        # exclude=True,
    )
    active: bool | None = False
    created_by: int | None = None


class ProductCreate(ProductBase):
    """The model for creating a new Product object"""

    # product_details: List[ProductDetailCreate]


class ProductUpdate(ProductBase):
    """The model for updating the Product object"""

    # active: bool
    # product_details: List[ProductDetailUpdate]


class ProductResponse(ProductBase):
    """The model for reading the Product object"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    user: UserResponse


class ProductValidate(BaseModel):
    """The base model for the validation of the Product object"""

    name: str | None = None
    version: str | None = None
    description: str | None = None
    repository_url: str | None = None
    repository_username: str | None = None
    repository_password: str | None = None
