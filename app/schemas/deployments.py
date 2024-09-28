from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.stacks import StackResponse
from app.schemas.teams import TeamResponse
from app.schemas.users import UserResponse


class DeploymentBase(BaseModel):
    """The base model for the Deployment object"""

    model_config = ConfigDict(
        str_min_length=1,
        str_max_length=256,
        str_strip_whitespace=True,
    )

    name: str
    stack_id: int
    team_id: int
    user_id: int


class DeploymentCreate(DeploymentBase):
    """The model for creating a new Deployment object"""

    pass


class DeploymentUpdate(DeploymentBase):
    """The model for updating the Deployment object"""

    active: bool


class DeploymentResponse(DeploymentBase):
    """The model for reading the Deployment object"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    stack: StackResponse
    user: UserResponse
    team: TeamResponse
