from sqlalchemy import String, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class User(Base):
    username: Mapped[str] = mapped_column(String, nullable=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger)

    balance: Mapped[int] = mapped_column(Integer)

    referral_user_count: Mapped[int] = mapped_column(Integer, nullable=True)

    connect_referral_user: Mapped[int] = mapped_column(Integer, nullable=True)

    balance_bonus: Mapped[list["BalanceBonus"]] = relationship(
        "BalanceBonus",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    requests_count: Mapped[list["RequestCount"]] = relationship(
        "RequestCount",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    requests: Mapped[list["RequestAI"]] = relationship(
        "RequestAI",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan",
    )