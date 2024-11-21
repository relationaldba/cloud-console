from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, conint


class AWSEC2InstanceClassEnum(str, Enum):
    burstable2 = "BURSTABLE2"
    burstable3 = "BURSTABLE3"
    burstable3_amd = "BURSTABLE3_AMD"
    burstable4_graviton = "BURSTABLE4_GRAVITON"


class AWSEC2InstanceSizeEnum(str, Enum):
    nano = "NANO"
    micro = "MICRO"
    small = "SMALL"
    medium = "MEDIUM"
    large = "LARGE"
    xlarge = "XLARGE"
    xlarge2 = "XLARGE2"


class StackPropertyBase(BaseModel):
    name: Literal["instance_class", "instance_size", "disk_size"]
    value: AWSEC2InstanceClassEnum | AWSEC2InstanceSizeEnum | conint(le=100) # type: ignore


# class StackPropertyBase(BaseModel):
#     """The base model for the StackProperty object"""

#     model_config = ConfigDict(
#         str_min_length=1,
#         str_max_length=256,
#         str_strip_whitespace=True,
#     )

#     name: str = "Any Name" or "Any Name"
#     value: str = Field(max_length=512)


class StackPropertyCreate(StackPropertyBase):
    """The model for creating a new StackProperty object"""

    pass


class StackPropertyUpdate(StackPropertyBase):
    """The model for updating the StackProperty object"""

    pass


class StackPropertyResponse(BaseModel):
    """The model for reading the StackProperty object"""

    model_config = ConfigDict(from_attributes=True)

    name: str
    value: str
