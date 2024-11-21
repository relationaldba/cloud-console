from datetime import datetime
from typing import Annotated, List

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from .product_properties import ProductPropertyResponse, ProductPropertyCreate
from .stack_properties import StackPropertyCreate, StackPropertyResponse


class DeploymentBase(BaseModel):
    """The base model for the Deployment object"""

    model_config = ConfigDict(
        str_min_length=3,
        str_max_length=256,
        str_strip_whitespace=True,
    )

    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, to_upper=True),
    ]
    description: str | None = Field(default=None, min_length=0)
    # status: str | None = Field(default="QUEUED")
    environment_id: int
    stack_id: int
    product_id: int
    stack_properties: List[StackPropertyCreate] | None = []
    product_properties: List[ProductPropertyCreate] | None = []


class DeploymentCreate(DeploymentBase):
    """The model for creating a new Deployment object"""

    pass


class DeploymentUpdate(DeploymentBase):
    """The model for updating the Deployment object"""

    pass


class DeploymentResponse(BaseModel):
    """The model for reading the Deployment object"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    created_by: int
    environment_id: int
    stack_id: int
    product_id: int
    stack_properties: list[StackPropertyResponse] | None
    product_properties: list[ProductPropertyResponse] | None


class DeploymentValidate(BaseModel):
    """The base model for the validation of the Deployment object"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )
    name: str | None = None
    environment_id: int | None = None
    stack_id: int | None = None
    product_id: int | None = None
