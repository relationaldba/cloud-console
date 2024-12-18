from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import TIMESTAMP, Boolean, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .deployments import Deployment
    from .environments import Environment
    from .products import Product


class User(Base):
    """ORM Class that represents the `users` table"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        name="id",
        type_=Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    first_name: Mapped[str] = mapped_column(
        name="first_name",
        type_=String(128),
        nullable=False,
    )
    last_name: Mapped[str] = mapped_column(
        name="last_name",
        type_=String(128),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        name="email",
        type_=String(512),
        nullable=True,
        unique=True,
    )
    password: Mapped[str] = mapped_column(
        name="password",
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
    last_login_at: Mapped[datetime] = mapped_column(
        name="last_login_at",
        type_=TIMESTAMP(timezone=True),
        nullable=True,
    )
    deployments: Mapped[List["Deployment"]] = relationship(
        back_populates="user",
    )
    products: Mapped[List["Product"]] = relationship(
        back_populates="user",
    )
    environments: Mapped[List["Environment"]] = relationship(
        back_populates="user",
    )