from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict

from app.schemas.users import UserResponse


class TeamBase(BaseModel):
    """The base model for the Team object"""

    model_config = ConfigDict(
        str_min_length=1,
        str_max_length=256,
        str_strip_whitespace=True,
    )

    name: str


class TeamCreate(TeamBase):
    """The model for creating the Team object"""

    pass


class TeamUpdate(TeamBase):
    """The model for updating the Team object"""

    active: bool


class TeamResponse(TeamBase):
    """The model for reading the Team object"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool
    created_at: datetime
    updated_at: datetime
    users: List[UserResponse]
