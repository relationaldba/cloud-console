from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .deployments import Deployment
    from .environments import Environment
    from .stacks import Stack
    from .users import User


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
        type_=String(64),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        name="name",
        type_=String(64),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        name="description",
        type_=String(256),
        nullable=True,
    )
    active: Mapped[bool] = mapped_column(
        name="active",
        type_=Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    created_by: Mapped[int] = mapped_column(
        ForeignKey(
            column="users.id",
            name="fk_cloudproviders_users",
            ondelete="CASCADE",
        ),
        name="created_by",
        nullable=False,
    )
    user: Mapped["User"] = relationship(
        back_populates="cloudproviders",
    )
    created_at: Mapped[datetime] = mapped_column(
        name="created_at",
        type_=TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        name="updated_at",
        type_=TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    environments: Mapped[List["Environment"]] = relationship(
        back_populates="cloudprovider",
    )
    stacks: Mapped[List["Stack"]] = relationship(
        back_populates="cloudprovider",
    )
    deployments: Mapped["Deployment"] = relationship(
        back_populates="cloudprovider",
    )
