from datetime import datetime
import enum
from typing import TYPE_CHECKING, List

from sqlalchemy import (
    TIMESTAMP,
    ForeignKey,
    Integer,
    String,
    func,
    Enum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .environments import Environment
    from .product_properties import ProductProperty
    from .products import Product
    from .stack_properties import StackProperty
    from .stacks import Stack
    from .users import User


class DeploymentStatusEnum(str, enum.Enum):
    QUEUED = "QUEUED"  # Default
    SYNTHESIZING = "SYNTHESIZING"
    CREATING = "CREATING"
    INSTALLING = "INSTALLING"
    ONLINE = "ONLINE"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    DELETING = "DELETING"
    DELETED = "DELETED"
    FAILED = "FAILED"
    ERROR = "ERROR"
    RESTARTING = "RESTARTING"
    UPGRADING = "UPGRADING"
    ROLLINGBACK = "ROLLINGBACK"


class Deployment(Base):
    """ORM Class that represents the `deployments` table"""

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
    description: Mapped[str] = mapped_column(
        name="description",
        type_=String(256),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        name="status",
        type_=String(128),
        nullable=False,
        default=DeploymentStatusEnum.QUEUED.value,
        server_default=DeploymentStatusEnum.QUEUED.value,
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
    deleted_at: Mapped[datetime] = mapped_column(
        name="deleted_at",
        type_=TIMESTAMP(timezone=True),
        nullable=True,
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
    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="products.id",
            name="fk_deployments_products",
            ondelete="CASCADE",
        ),
        name="product_id",
        nullable=False,
    )
    product: Mapped["Product"] = relationship(
        back_populates="deployments",
    )
    stack_properties: Mapped[List["StackProperty"]] = relationship(
        back_populates="deployment",
        cascade="all, delete-orphan",
    )
    product_properties: Mapped[List["ProductProperty"]] = relationship(
        back_populates="deployment",
        cascade="all, delete-orphan",
    )
