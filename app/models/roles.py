from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

if TYPE_CHECKING:
    pass


class Role(Base):
    """ORM Class that represents the `roles` table"""

    __tablename__ = "roles"

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
    group_id: Mapped[int] = mapped_column(
        ForeignKey(column="groups.id", name="fk_roles_groups", ondelete="CASCADE"),
        name="group_id",
        nullable=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey(column="users.id", name="fk_roles_users", ondelete="CASCADE"),
        name="user_id",
        nullable=True,
    )
    environment_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="environments.id", name="fk_roles_environments", ondelete="CASCADE"
        ),
        name="environment_id",
        nullable=True,
    )
