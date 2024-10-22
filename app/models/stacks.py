from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .cloudproviders import CloudProvider
    from .deployments import Deployment
    from .users import User


class Stack(Base):
    """ORM Class that represents the `stacks` table"""

    __tablename__ = "stacks"

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
    class_name: Mapped[str] = mapped_column(
        name="class_name",
        type_=String(128),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        name="description",
        type_=String(512),
        nullable=False,
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
            name="fk_stacks_users",
            ondelete="CASCADE",
        ),
        name="created_by",
        nullable=False,
    )
    user: Mapped["User"] = relationship(
        back_populates="stacks",
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
            name="fk_stacks_cloudproviders",
            ondelete="CASCADE",
        ),
        name="cloudprovider_id",
        nullable=False,
    )
    cloudprovider: Mapped["CloudProvider"] = relationship(
        back_populates="stacks",
    )
    deployments: Mapped["Deployment"] = relationship(
        back_populates="stack",
    )
    # stack_details: Mapped[List["StackDetail"]] = relationship(
    #     back_populates="stack",
    # )
