from pydantic import BaseModel, ConfigDict

from .product_properties import ProductPropertyCreate
from .stack_properties import StackPropertyCreate


class DeploymentPropertyBase(BaseModel):
    """The base model for the DeploymentProperty object"""

    model_config = ConfigDict(
        str_min_length=1,
        str_max_length=256,
        str_strip_whitespace=True,
    )

    stack_properties: list[StackPropertyCreate] | None = None
    product_properties: list[ProductPropertyCreate] | None = None


class DeploymentPropertyCreate(DeploymentPropertyBase):
    """The model for creating a new DeploymentProperty object"""

    pass


class DeploymentPropertyUpdate(DeploymentPropertyBase):
    """The model for updating the DeploymentProperty object"""

    pass


class DeploymentPropertyResponse(BaseModel):
    """The model for reading the DeploymentProperty object"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    stack_properties: list[StackPropertyCreate] | None = []
    product_properties: list[ProductPropertyCreate] | None = []
