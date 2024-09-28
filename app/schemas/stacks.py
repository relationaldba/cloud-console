from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict

from app.schemas.stack_details import StackDetailResponse


class StackBase(BaseModel):
    """The base model for the Stack object"""

    model_config = ConfigDict(
        str_min_length=1,
        str_max_length=256,
        str_strip_whitespace=True,
    )

    name: str


class StackCreate(StackBase):
    """The model for creating a new Stack object"""

    pass


class StackUpdate(StackBase):
    """The model for updating the Stack object"""

    active: bool


class StackResponse(StackBase):
    """The model for reading the Stack object"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    stack_details: List[StackDetailResponse]
