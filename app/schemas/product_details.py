from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProductDetailBase(BaseModel):
    """The base model for the ProductDetail object"""

    model_config = ConfigDict(
        str_min_length=1,
        str_max_length=256,
        str_strip_whitespace=True,
    )

    name: str
    value: str
    product_id: int


class ProductDetailCreate(ProductDetailBase):
    """The model for creating a new ProductDetail object"""

    pass


class ProductDetailUpdate(ProductDetailBase):
    """The model for updating the ProductDetail object"""

    active: bool


class ProductDetailResponse(ProductDetailBase):
    """The model for reading the ProductDetail object"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool
    created_at: datetime
    updated_at: datetime
