from datetime import datetime
from typing import TYPE_CHECKING, List

from pydantic import HttpUrl
from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    # from .product_details import ProductDetail
    # from .stack_details import StackDetail
    from .users import User


class Product(Base):
    """ORM Class that represents the `products` table"""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        name="id",
        type_=Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        name="name",
        type_=String(256),
        nullable=False,
    )
    version: Mapped[str] = mapped_column(
        name="version",
        type_=String(16),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        name="description",
        type_=String(256),
        nullable=True,
    )
    repository_url: Mapped[HttpUrl] = mapped_column(
        name="repository_url",
        type_=String(256),
        nullable=False,
    )
    repository_username: Mapped[str] = mapped_column(
        name="repository_username",
        type_=String(256),
        nullable=False,
    )
    repository_password: Mapped[str] = mapped_column(
        name="repository_password",
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
        ForeignKey(column="users.id", name="fk_products_users", ondelete="CASCADE"),
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
        back_populates="products",
    )
    # product_details: Mapped[List["ProductDetail"]] = relationship(
    #     back_populates="product",
    # )
    # stack_details: Mapped[List["StackDetail"]] = relationship(
    #     back_populates="product",
    # )

    __table_args__ = (Index("ix_products_id_active", "id", "active"),)

