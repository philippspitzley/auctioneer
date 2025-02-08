from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field, Relationship, SQLModel

from ..models.product_model import Product
from ..utils import get_current_timestamp

# Import Product model only for type checking to avoid circular imports
if TYPE_CHECKING:
    from .product_model import Product
    from .user_model import User


# TODO: generate UUI


class State(str, Enum):
    setup = "setup"
    live = "live"
    finished = "finished"


class AuctionBase(SQLModel):
    owner_id: int = Field(foreign_key="user.id", ondelete="SET NULL")
    state: State = Field(default=State.setup)


class AuctionPublic(AuctionBase):
    id: int
    product_id: int
    start_time: datetime | None
    end_time: datetime | None
    starting_price: float | None
    min_bid: float | None
    instant_buy_price: float | None
    buyer_id: int | None
    sold: bool
    sold_price: float | None


class Auction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    product_id: int | None = Field(
        foreign_key="product.id", ondelete="SET NULL"
    )
    state: State = Field(default=State.setup)
    start_time: datetime | None = Field(default=None)
    end_time: datetime | None = Field(default=None)
    starting_price: float | None = Field(default=None)
    min_bid: float | None = Field(default=None)
    instant_buy_price: float | None = Field(default=None)
    buyer_id: int | None = Field(default=None, foreign_key="user.id")
    sold: bool = Field(default=False)
    sold_price: float | None = Field(default=None)
    created_at: datetime = Field(default_factory=get_current_timestamp)
    updated_at: datetime | None = Field(default=None)

    bids: Mapped[list["Bid"]] = Relationship(
        sa_relationship=relationship(back_populates="auction")
    )

    products: Mapped[list["Product"]] = Relationship(
        sa_relationship=relationship(back_populates="auction")
    )

    owner: Optional["User"] = Relationship(
        sa_relationship=relationship(
            back_populates="auctions",
            foreign_keys="[Auction.owner_id]",
        )
    )

    # TODO: Due to a bug in sqlalchemy, the following line does not work
    # bids: list[Bid] = Relationship(
    #     back_populates="auction", cascade_delete=True
    # )


class AuctionCreate(AuctionBase):
    pass


class AuctionUpdate(SQLModel):
    state: State | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    starting_price: float | None = None
    min_bid: float | None = None
    instant_buy_price: float | None = None
    sold: bool | None = None
    sold_price: float | None = None
    updated_at: datetime = Field(default_factory=get_current_timestamp)


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
