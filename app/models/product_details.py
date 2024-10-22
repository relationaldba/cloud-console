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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .products import Product


class ProductDetail(Base):
    """ORM Class that represents the `product_details` table"""

    __tablename__ = "product_details"

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
    # product_id: Mapped[int] = mapped_column(
    #     ForeignKey(
    #         column="products.id", name="fk_product_details_products", ondelete="CASCADE"
    #     ),
    #     name="product_id",
    #     nullable=False,
    # )
    # product: Mapped["Product"] = relationship(
    #     back_populates="product_details",
    # )
