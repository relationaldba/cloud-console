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
    from .environments import Environment


class EnvironmentDetail(Base):
    """ORM Class that represents the `environment_details` table"""

    __tablename__ = "environment_details"

    id: Mapped[int] = mapped_column(
        name="id",
        type_=Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
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
    # environment_id: Mapped[int] = mapped_column(
    #     ForeignKey(
    #         column="environments.id",
    #         name="fk_environment_details_environments",
    #         ondelete="CASCADE",
    #     ),
    #     name="environment_id",
    #     nullable=False,
    # )
    # environment: Mapped["Environment"] = relationship(
    #     back_populates="environment_details",
    # )
