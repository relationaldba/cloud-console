from pydantic import BaseModel, ConfigDict
from typing import Literal, Union

class ProductPropertyCreate(BaseModel):
    """
    The base model for the ProductPropertyFile object
    The value should be a base64 encoded properties file
    """

    model_config = ConfigDict(
        str_min_length=1,
        str_strip_whitespace=True,
    )

    name: Literal["properties_base64"]
    value: str

# class ProductPropertyItemBase(BaseModel):
#     """
#     The base model for the ProductPropertyItem object
#     The property should be a name and value
#     """

#     model_config = ConfigDict(
#         str_min_length=1,
#         str_strip_whitespace=True,
#     )

#     name: str
#     value: str

# ProductPropertyCreate = ProductPropertyFileBase | ProductPropertyItemBase

# class ProductPropertyCreate(ProductPropertyBase):
#     """The model for creating a new ProductProperty object"""
    
#     pass


# class ProductPropertyUpdate(ProductPropertyBase):
#     """The model for updating the ProductProperty object"""

#     # pass


class ProductPropertyResponse(BaseModel):
    """The model for reading the ProductProperty object"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    value: str
