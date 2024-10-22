from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

# from .environment_details import EnvironmentDetailCreate
from .cloudproviders import CloudProviderMiniResponse

class EnvironmentBase(BaseModel):
    """The base model for the Environment object"""

    model_config = ConfigDict(
        str_min_length=3,
        str_max_length=256,
        str_strip_whitespace=True,
    )

    name: str
    cloudprovider_id: int
    aws_account_id: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str

    # environment_details: List["EnvironmentDetailCreate"] | List[None] = []


class EnvironmentCreate(EnvironmentBase):
    """The model for creating a new Environment object"""

    # environment_details: List[EnvironmentDetailCreate]
    pass


class EnvironmentUpdate(EnvironmentBase):
    """The model for updating the Environment object"""

    active: bool | None = False
    # environment_details: List[EnvironmentDetailUpdate]


class EnvironmentResponse(BaseModel):
    """The model for reading the Environment object"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    aws_account_id: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    created_at: datetime
    updated_at: datetime
    creator: EmailStr

    cloudprovider: CloudProviderMiniResponse


class EnvironmentMiniResponse(BaseModel):
    """The model for returning a short Environment object"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    aws_region: str


class EnvironmentValidate(BaseModel):
    """The base model for the validation of the Environment object"""

    name: str | None = None
    aws_account_id: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
