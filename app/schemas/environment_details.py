from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EnvironmentDetailBase(BaseModel):
    """The base model for the EnvironmentDetail object"""

    model_config = ConfigDict(
        str_min_length=1,
        str_max_length=256,
        str_strip_whitespace=True,
    )
    environment_id: int | None = None
    name: str
    value: str
    


class EnvironmentDetailCreate(EnvironmentDetailBase):
    """The model for creating a new EnvironmentDetail object"""

    pass


class EnvironmentDetailUpdate(EnvironmentDetailBase):
    """The model for updating the EnvironmentDetail object"""

    active: bool


class EnvironmentDetailResponse(EnvironmentDetailBase):
    """The model for reading the EnvironmentDetail object"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool
    created_at: datetime
    updated_at: datetime


class EnvironmentDetailValidate(BaseModel):
    """The base model for the EnvironmentDetail object"""

    name: str | None = None
    value: str | None = None