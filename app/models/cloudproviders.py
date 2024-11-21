from typing import TYPE_CHECKING, List

from sqlalchemy import (
    Boolean,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .deployments import Deployment
    from .environments import Environment
    from .stacks import Stack


class CloudProvider(Base):
    """ORM Class that represents the `cloudproviders` table"""

    __tablename__ = "cloudproviders"

    id: Mapped[int] = mapped_column(
        name="id",
        type_=Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )
    code: Mapped[str] = mapped_column(
        name="code",
        type_=String(32),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        name="name",
        type_=String(128),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        name="description",
        type_=String(512),
        nullable=True,
    )
    active: Mapped[bool] = mapped_column(
        name="active",
        type_=Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    environments: Mapped[List["Environment"]] = relationship(
        back_populates="cloudprovider",
    )
    stacks: Mapped[List["Stack"]] = relationship(
        back_populates="cloudprovider",
    )