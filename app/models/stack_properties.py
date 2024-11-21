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
    from .deployments import Deployment
    from .stacks import Stack


class StackProperty(Base):
    """ORM Class that represents the `stack_properties` table"""

    __tablename__ = "stack_properties"

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
    value: Mapped[str] = mapped_column(
        name="value",
        type_=String(4096),
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
    stack_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="stacks.id",
            name="fk_stack_properties_stacks",
            ondelete="CASCADE",
        ),
        name="stack_id",
        nullable=False,
    )
    stack: Mapped["Stack"] = relationship(
        back_populates="stack_properties",
    )
    deployment_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="deployments.id",
            name="fk_stack_properties_deployments",
            ondelete="CASCADE",
        ),
        name="deployment_id",
        nullable=False,
    )
    deployment: Mapped["Deployment"] = relationship(
        back_populates="stack_properties",
    )
