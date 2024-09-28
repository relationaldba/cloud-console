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
    from .products import Product
    from .services import Service
    from .stacks import Stack


class StackDetail(Base):
    """ORM Class that represents the `stack_details` table"""

    __tablename__ = "stack_details"

    id: Mapped[int] = mapped_column(
        name="id",
        type_=Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
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
    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="products.id",
            name="fk_stack_details_products",
            ondelete="CASCADE",
        ),
        name="product_id",
        nullable=False,
    )
    product: Mapped["Product"] = relationship(
        back_populates="stack_details",
    )
    service_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="services.id",
            name="fk_stack_details_services",
            ondelete="CASCADE",
        ),
        name="service_id",
        nullable=False,
    )
    service: Mapped["Service"] = relationship(
        back_populates="stack_details",
    )
    service_type: Mapped[str] = mapped_column(
        name="service_type",
        type_=String(128),
        nullable=False,
    )
    stack_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="stacks.id",
            name="fk_stack_details_stacks",
            ondelete="CASCADE",
        ),
        name="stack_id",
        nullable=False,
    )
    stack: Mapped["Stack"] = relationship(
        back_populates="stack_details",
    )
