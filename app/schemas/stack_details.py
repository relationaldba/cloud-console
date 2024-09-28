from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.products import ProductResponse
from app.schemas.services import ServiceResponse


class StackDetailBase(BaseModel):
    """The base model for the StackDetail object"""

    model_config = ConfigDict(
        str_min_length=1,
        str_max_length=256,
        str_strip_whitespace=True,
    )

    product_id: int
    service_id: int
    stack_id: int


class StackDetailCreate(StackDetailBase):
    """The model for creating a new StackDetail object"""

    pass


class StackDetailUpdate(StackDetailBase):
    """The model for updating the StackDetail object"""

    active: bool


class StackDetailResponse(StackDetailBase):
    """The model for reading the StackDetail object"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    product: ProductResponse
    service: ServiceResponse
