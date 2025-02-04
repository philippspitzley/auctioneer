from __future__ import annotations  # to use forward references

from datetime import datetime

from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field, Relationship, SQLModel

from ..utils.helper import get_current_timestamp

# TODO: generate UUI


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str | None = Field(default=None)

    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)

    categories: Mapped[list[Category]] = Relationship(
        sa_relationship=relationship(back_populates="product")
    )

    # TODO: Due to a bug in sqlalchemy, the following line does not work
    # categories: list[Category] = Relationship(
    #     back_populates="product", cascade_delete=True
    # )


class ProductCreate(Product):
    created_at: datetime = Field(default_factory=get_current_timestamp)


class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: str | None = Field(default=None)

    product_id: int | None = Field(
        default=None, foreign_key="product.id", ondelete="SET NULL"
    )
    product: Product | None = Relationship(
        sa_relationship=relationship(back_populates="categories")
    )

    # TODO: Due to a bug in sqlalchemy, the following line does not work
    # product: Product | None = Relationship(back_populates="categories")
