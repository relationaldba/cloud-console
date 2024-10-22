from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.environments import EnvironmentResponse
from app.schemas.stacks import StackResponse


class DeploymentBase(BaseModel):
    """The base model for the Deployment object"""

    model_config = ConfigDict(
        str_min_length=1,
        str_max_length=256,
        str_strip_whitespace=True,
    )

    name: str
    cloudprovider_id: int
    stack_id: int
    environment_id: int
    status: str | None = Field(default="pending")


class DeploymentCreate(DeploymentBase):
    """The model for creating a new Deployment object"""

    pass


class DeploymentUpdate(DeploymentBase):
    """The model for updating the Deployment object"""

    pass


class DeploymentResponse(DeploymentBase):
    """The model for reading the Deployment object"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

    stack: StackResponse
    environment: EnvironmentResponse


class DeploymentValidate(BaseModel):
    """The base model for the validation of the Deployment object"""

    name: str | None = None
    cloudprovider: str | None = None
    aws_account_id: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region: str | None = None
