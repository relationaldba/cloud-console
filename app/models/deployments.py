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
    from .stacks import Stack
    from .users import User


class Deployment(Base):
    """ORM Class that represents the `stacks` table"""

    __tablename__ = "deployments"

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
    stack_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="stacks.id",
            name="fk_deployments_stacks",
            ondelete="CASCADE",
        ),
        name="stack_id",
        nullable=False,
    )
    stack: Mapped["Stack"] = relationship(
        back_populates="deployments",
    )
    # team_id: Mapped[int] = mapped_column(
    #     ForeignKey(
    #         column="teams.id",
    #         name="fk_deployments_teams",
    #         ondelete="CASCADE",
    #     ),
    #     name="team_id",
    #     nullable=False,
    # )
    # team: Mapped["Team"] = relationship(
    #     back_populates="deployments",
    # )
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="users.id",
            name="fk_deployments_users",
            ondelete="CASCADE",
        ),
        name="user_id",
        nullable=False,
    )
    user: Mapped["User"] = relationship(
        back_populates="deployments",
    )


# TODO: add deployment created by user
