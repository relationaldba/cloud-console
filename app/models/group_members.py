from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, ForeignKey, Index, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .groups import Group
    from .users import User


class GroupMember(Base):
    """ORM Class that represents the `group_members` table"""

    __tablename__ = "group_members"

    id: Mapped[int] = mapped_column(
        name="id",
        type_=Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey(
            name="fk_group_members_groups",
            column="groups.id",
            ondelete="CASCADE",
        ),
        name="group_id",
        nullable=False,
    )
    group: Mapped["Group"] = relationship()
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            name="fk_group_members_users",
            column="users.id",
            ondelete="CASCADE",
        ),
        name="user_id",
        nullable=False,
    )
    user: Mapped["User"] = relationship()
    created_at: Mapped[datetime] = mapped_column(
        name="created_at",
        type_=TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index(
            "uq_group_members_group_id_user_id",
            "group_id",
            "user_id",
            unique=True,
        ),
    )
