from __future__ import annotations  # to use forward references

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field, Relationship, SQLModel

from .utils import get_current_timestamp

# TODO: generate UUI
# TODO: change relationship back to sqlmodel, if bug in sqlalchemy/sqlmodel is fixed
# https://github.com/fastapi/sqlmodel/discussions/771
# Downgrading sqlalchmey to 2.0.36 does not fix the bug


class Role(str, Enum):
    admin = "admin"
    user = "member"
    guest = "guest"


class State(str, Enum):
    setup = "setup"
    live = "live"
    finished = "finished"


class User(SQLModel, table=True):
    # id: None is only for pydantic, because in code we use id = None. The id is generated py postgres when saving it to the db. Might change it to uuid in the future.
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(index=True, unique=True)
    password_hash: str = Field()
    role: Role = Field(default=Role.guest)
    created_at: datetime = Field(default_factory=get_current_timestamp)
    updated_at: datetime | None = Field(default=None)


class Auction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    seller_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    state: State = Field(default=State.setup)
    start_time: datetime | None = Field(default=None)
    end_time: datetime | None = Field(default=None)
    starting_price: float | None = Field(default=None)
    min_bid: float | None = Field(default=None)
    instant_buy_price: float | None = Field(default=None)
    buyer_id: int | None = Field(default=None, foreign_key="user.id")
    sold: bool = Field(default=False)
    sold_price: float | None = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime | None = Field(default=None)

    bids: Mapped[list[Bid]] = Relationship(
        sa_relationship=relationship(back_populates="auction")
    )

    # TODO: Due to a bug in sqlalchemy, the following line does not work
    # bids: list[Bid] = Relationship(
    #     back_populates="auction", cascade_delete=True
    # )


class Bid(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    bidder_id: int = Field(foreign_key="user.id")
    amount: float
    created_at: datetime = Field(default_factory=get_current_timestamp)

    auction_id: int | None = Field(
        foreign_key="auction.id", ondelete="CASCADE"
    )
    auction: Auction | None = Relationship(
        sa_relationship=relationship(back_populates="bids")
    )

    # TODO: Due to a bug in sqlalchemy, the following line does not work
    # auction: Auction | None = Relationship(back_populates="bids")


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str | None = Field(default=None)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime | None = Field(default=None)

    categories: Mapped[list[Category]] = Relationship(
        sa_relationship=relationship(back_populates="product")
    )

    # TODO: Due to a bug in sqlalchemy, the following line does not work
    # categories: list[Category] = Relationship(
    #     back_populates="product", cascade_delete=True
    # )


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
