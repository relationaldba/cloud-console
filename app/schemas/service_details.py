from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ServiceDetailBase(BaseModel):
    """The base model for the ServiceDetail object"""

    model_config = ConfigDict(
        str_min_length=1,
        str_max_length=256,
        str_strip_whitespace=True,
    )

    name: str
    value: str
    service_id: int


class ServiceDetailCreate(ServiceDetailBase):
    """The model for creating a new ServiceDetail object"""

    pass


class ServiceDetailUpdate(ServiceDetailBase):
    """The model for updating the ServiceDetail object"""

    active: bool


class ServiceDetailResponse(ServiceDetailBase):
    """The model for reading the ServiceDetail object"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool
    created_at: datetime
    updated_at: datetime
