from pydantic import BaseModel, ConfigDict, Field


class CloudProviderBase(BaseModel):
    """The base model for the CloudProvider object"""

    model_config = ConfigDict(
        str_min_length=3,
        str_max_length=256,
        str_strip_whitespace=True,
    )
    code: str
    name: str
    description: str | None = Field(default=None, min_length=0)


class CloudProviderCreate(CloudProviderBase):
    """The model for creating a new CloudProvider object"""

    pass


class CloudProviderUpdate(BaseModel):
    """The model for updating the CloudProvider object"""

    active: bool


class CloudProviderResponse(CloudProviderBase):
    """The model for reading the CloudProvider object"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    active: bool


class CloudProviderMiniResponse(BaseModel):
    """The model for returning a short CloudProvider object"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
