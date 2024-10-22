from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .service_details import ServiceDetail
    from .stack_details import StackDetail


class Service(Base):
    """ORM Class that represents the `services` table"""

    __tablename__ = "services"

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
    type: Mapped[str] = mapped_column(
        name="type",
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
    # service_details: Mapped[List["ServiceDetail"]] = relationship(
    #     back_populates="service",
    # )
    # stack_details: Mapped[List["StackDetail"]] = relationship(
    #     back_populates="service",
    # )


# TODO: add service created by user