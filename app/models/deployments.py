from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    TIMESTAMP,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .cloudproviders import CloudProvider
    from .environments import Environment
    from .stacks import Stack
    from .users import User


class Deployment(Base):
    """ORM Class that represents the `stacks` table"""

    __tablename__ = "deployments"

    id: Mapped[int] = mapped_column(
        name="id",
        type_=Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        name="name",
        type_=String(128),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        name="status",
        type_=String(128),
        nullable=False,
    )
    created_by: Mapped[int] = mapped_column(
        ForeignKey(
            column="users.id",
            name="fk_deployments_users",
            ondelete="CASCADE",
        ),
        name="user_id",
        nullable=False,
    )
    user: Mapped["User"] = relationship(
        back_populates="deployments",
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
    cloudprovider_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="cloudproviders.id",
            name="fk_deployments_cloudproviders",
            ondelete="CASCADE",
        ),
        name="cloudprovider_id",
        nullable=False,
    )
    cloudprovider: Mapped["CloudProvider"] = relationship(
        back_populates="deployments",
    )
    environment_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="environments.id",
            name="fk_deployments_environments",
            ondelete="CASCADE",
        ),
        name="environment_id",
        nullable=False,
    )
    environment: Mapped["Environment"] = relationship(
        back_populates="deployments",
    )
    stack_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="stacks.id",
            name="fk_deployments_stacks",
            ondelete="CASCADE",
        ),
        name="stack_id",
        nullable=False,
    )
    stack: Mapped["Stack"] = relationship(
        back_populates="deployments",
    )
