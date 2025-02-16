from datetime import datetime
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field, Relationship, SQLModel

from app.utils import get_current_timestamp

# Import Product model only for type checking to avoid circular imports
if TYPE_CHECKING:
    from .auction_model import Auction
    from .user_model import User

# TODO: change model to only show name and description
# TODO: generate UUI
# TODO: CRUD pydantic classes


class ProductBase(SQLModel):
    owner_id: int
    name: str
    description: str | None


class ProductCreate(ProductBase):
    pass


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(
        foreign_key="user.id",
        ondelete="SET NULL",
        nullable=True,
    )
    name: str = Field(index=True)
    description: str | None = Field(default=None)
    created_at: datetime | None = Field(
        default_factory=get_current_timestamp,
        sa_column=sa.Column(sa.DateTime(timezone=True)),
    )
    updated_at: datetime | None = Field(
        default=None, sa_column=sa.Column(sa.DateTime(timezone=True))
    )

    # Relationships
    categories: Mapped[list["Category"]] = Relationship(
        sa_relationship=relationship(back_populates="product")
    )
    auction: Optional["Auction"] = Relationship(
        sa_relationship=relationship(back_populates="products")
    )
    owner: Optional["User"] = Relationship(
        sa_relationship=relationship(back_populates="products")
    )

    # TODO: Due to a bug in sqlalchemy, the following line does not work
    # categories: list[Category] = Relationship(
    #     back_populates="product", cascade_delete=True
    # )


# class ProductPublic(Product):
#     pass


class Category(SQLModel, table=True):
    # id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, primary_key=True)
    description: str | None = Field(default=None)

    product_id: int | None = Field(
        default=None, foreign_key="product.id", ondelete="SET NULL"
    )
    product: Product | None = Relationship(
        sa_relationship=relationship(back_populates="categories")
    )

    # TODO: Due to a bug in sqlalchemy, the following line does not work
    # product: Product | None = Relationship(back_populates="categories")
