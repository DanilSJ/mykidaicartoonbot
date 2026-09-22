from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class User(Base):
    username: Mapped[str] = mapped_column(String, nullable=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger)
