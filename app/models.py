from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    _abstract = True


class Car(Base):
    __tablename__ = "cars"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url: Mapped[str] = mapped_column(unique=True)
    title: Mapped[str] = mapped_column(nullable=False)
    price_usd: Mapped[int] = mapped_column(nullable=False)
    odometer: Mapped[int] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(nullable=False)
    phone_number: Mapped[str] = mapped_column(nullable=False)
    image_url: Mapped[str] = mapped_column(nullable=False)
    images_count: Mapped[int] = mapped_column(nullable=False)
    car_number: Mapped[str] = mapped_column(nullable=False)
    car_vin: Mapped[str] = mapped_column(nullable=False)
    datetime_found: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
