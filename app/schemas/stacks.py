from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .cloudproviders import CloudProviderMiniResponse

# from app.schemas.stack_details import StackDetailResponse


class StackBase(BaseModel):
    """The base model for the Stack object"""

    model_config = ConfigDict(
        str_min_length=1,
        str_max_length=256,
        str_strip_whitespace=True,
    )

    name: str
    class_name: str
    description: str | None = Field(default=None, min_length=0)
    cloudprovider_id: int


class StackCreate(StackBase):
    """The model for creating a new Stack object"""

    pass


class StackUpdate(StackBase):
    """The model for updating the Stack object"""

    active: bool | None = False


class StackResponse(BaseModel):
    """The model for reading the Stack object"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    class_name: str
    description: str | None = Field(default=None, min_length=0)
    active: bool
    created_at: datetime
    updated_at: datetime
    creator: EmailStr

    # stack_details: List[StackDetailResponse]
    cloudprovider: CloudProviderMiniResponse


class StackValidate(BaseModel):
    """The base model for the validation of the Stack object"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    name: str | None = None
    class_name: str | None = None
    description: str | None = None
