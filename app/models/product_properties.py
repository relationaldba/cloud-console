from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .deployments import Deployment
    from .products import Product


class ProductProperty(Base):
    """ORM Class that represents the `product_properties` table"""

    __tablename__ = "product_properties"

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
        type_=String,
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
    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="products.id",
            name="fk_product_properties_products",
            ondelete="CASCADE",
        ),
        name="product_id",
        nullable=False,
    )
    product: Mapped["Product"] = relationship()
    deployment_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="deployments.id",
            name="fk_product_properties_deployments",
            ondelete="CASCADE",
        ),
        name="deployment_id",
        nullable=False,
    )
    deployment: Mapped["Deployment"] = relationship(
        back_populates="product_properties",
    )
