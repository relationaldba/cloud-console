from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict

from app.schemas.service_details import ServiceDetailResponse


class ServiceBase(BaseModel):
    """The base model for the Service object"""

    model_config = ConfigDict(
        str_min_length=1,
        str_max_length=256,
        str_strip_whitespace=True,
    )

    name: str


class ServiceCreate(ServiceBase):
    """The model for creating a new Service object"""

    pass


class ServiceUpdate(ServiceBase):
    """The model for updating the Service object"""

    active: bool


class ServiceResponse(ServiceBase):
    """The model for reading the Service object"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    service_details: List[ServiceDetailResponse]
