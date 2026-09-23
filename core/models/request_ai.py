from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class RequestAI(Base):
    prompt: Mapped[str] = mapped_column(String)
    audio: Mapped[bool] = mapped_column(Boolean)
    duration: Mapped[int] = mapped_column(Integer)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user: Mapped["User"] = relationship("User", back_populates="requests")
