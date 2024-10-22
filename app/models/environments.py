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
    # from .environment_details import EnvironmentDetail
    from .users import User
    from .cloudproviders import CloudProvider
    from .deployments import Deployment


class Environment(Base):
    """ORM Class that represents the `environments` table"""

    __tablename__ = "environments"

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
    cloudprovider_id: Mapped[int] = mapped_column(
        ForeignKey(column="cloudproviders.id", name="fk_environments_cloudproviders", ondelete="CASCADE"),
        name="cloudprovider_id",
        nullable=False,
    )
    aws_region: Mapped[str] = mapped_column(
        name="aws_region",
        type_=String(128),
        nullable=False,
    )
    aws_account_id: Mapped[str] = mapped_column(
        name="aws_account_id",
        type_=String(128),
        nullable=False,
    )
    aws_access_key_id: Mapped[str] = mapped_column(
        name="aws_access_key_id",
        type_=String(128),
        nullable=False,
    )
    aws_secret_access_key: Mapped[str] = mapped_column(
        name="aws_secret_access_key",
        type_=String(128),
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
        ForeignKey(column="users.id", name="fk_environments_users", ondelete="CASCADE"),
        name="created_by",
        nullable=False,
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
    user: Mapped["User"] = relationship(
        back_populates="environments",
    )
    cloudprovider: Mapped[List["CloudProvider"]] = relationship(
        back_populates="environments",
    )
    deployments: Mapped["Deployment"] = relationship(
        back_populates="environment",
    )
    # environment_details: Mapped[List["EnvironmentDetail"]] = relationship(
    #     back_populates="environment",
    #     cascade="all, delete-orphan",
    # )
