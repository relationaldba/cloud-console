from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

if TYPE_CHECKING:
    pass


class Secret(Base):
    """ORM Class that represents the `products` table"""

    __tablename__ = "secrets"

    id: Mapped[int] = mapped_column(
        name="id",
        type_=Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        name="name",
        type_=String,
        nullable=False,
    )
    value: Mapped[str] = mapped_column(
        name="value",
        type_=String,
        nullable=True,
    )
    description: Mapped[str] = mapped_column(
        name="description",
        type_=String,
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
        ForeignKey(column="users.id", name="fk_secrets_users", ondelete="CASCADE"),
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
