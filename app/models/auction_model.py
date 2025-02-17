from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field, Relationship, SQLModel

from ..utils import get_current_timestamp

# Import Product and User model only for type checking to avoid circular imports
if TYPE_CHECKING:
    from .product_model import Product
    from .user_model import User

# TODO: generate UUI
# TODO: handle delete of users, products and auction. How to handle foreign keys? Set null? cascade delete? set deleted username? keep auction and product. What if only owner or buyer is deleted?
# TODO: Due to a bug in sqlalchemy, the following line does not work
# bids: list[Bid] = Relationship(
#     back_populates="auction", cascade_delete=True
# )
# TODO: Due to a bug in sqlalchemy, the following line does not work
# auction: Auction | None = Relationship(back_populates="bids")


class State(str, Enum):
    setup = "setup"
    live = "live"
    finished = "finished"


class AuctionBase(SQLModel):
    owner_id: int
    product_id: int


class Auction(AuctionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(
        foreign_key="user.id",
        ondelete="SET NULL",
        nullable=True,
    )
    product_id: int | None = Field(
        foreign_key="product.id",
        ondelete="SET NULL",
        nullable=True,
    )
    buyer_id: int | None = Field(
        default=None,
        foreign_key="user.id",
        ondelete="SET NULL",
        nullable=True,
    )
    state: State = Field(default=State.setup)
    start_time: datetime | None = Field(
        default=None, sa_column=sa.Column(sa.DateTime(timezone=True))
    )
    end_time: datetime | None = Field(
        default=None, sa_column=sa.Column(sa.DateTime(timezone=True))
    )
    starting_price: float | None = Field(default=None)
    min_bid: float | None = Field(default=None)
    instant_buy_price: float | None = Field(default=None)
    sold: bool = Field(default=False)
    sold_price: float | None = Field(default=None)
    created_at: datetime = Field(
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False)
    )
    updated_at: datetime | None = Field(
        default=None, sa_column=sa.Column(sa.DateTime(timezone=True))
    )

    # Relationships
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
    buyer: Optional["User"] = Relationship(
        sa_relationship=relationship(
            back_populates="auctions",
            foreign_keys="[Auction.buyer_id]",
        )
    )

    # Methods
    def has_ended(self) -> bool:
        """
        Retrieve whether the auction has ended or not.

        This method checks whether the auction has already been finished or if its end time has passed.

        :return: :obj:`True` if the auction has ended or :obj:`False` if it has not.
        :rtype: bool
        """
        if not self.end_time or self.state != State.finished:
            return False

        return (
            self.state == State.finished
            or self.end_time < get_current_timestamp()
        )

    def get_highest_bidder(self):
        """
        Retrieve the highest bidder associated with the auction.

        If no bids are available, :obj:`None` is returned.

        :return: The highest bidder associated with the auction or :obj:`None` if no bids are available.
        :rtype: :class:`Bid` | None
        """
        if not self.bids:
            return None
        return max(self.bids, key=lambda bid: bid.amount)


class AuctionCreate(AuctionBase):
    starting_price: float | None = None
    min_bid: float | None = None
    instant_buy_price: float | None = None


class AuctionCreateFromProduct(SQLModel):
    starting_price: float | None = None
    min_bid: float | None = None
    instant_buy_price: float | None = None


class AuctionUpdate(AuctionCreate):
    owner_id: int | None = None
    product_id: int | None = None
    state: State | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    sold: bool | None = None
    sold_price: float | None = None
    buyer_id: int | None = None


class AuctionPublic(AuctionBase):
    id: int | None
    state: State
    product_id: int | None
    start_time: datetime | None
    end_time: datetime | None
    starting_price: float | None
    min_bid: float | None
    instant_buy_price: float | None
    buyer_id: int | None
    sold: bool
    sold_price: float | None


class AuctionLive(AuctionBase):
    id: int
    owner_id: int
    product_id: int
    buyer_id: int | None
    state: State = State.live
    start_time: datetime
    end_time: datetime
    starting_price: float
    min_bid: float | None
    instant_buy_price: float | None
    created_at: datetime
    updated_at: datetime | None


class Bid(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    bidder_id: int = Field(foreign_key="user.id")
    amount: float
    created_at: datetime = Field(
        default_factory=get_current_timestamp,
        sa_column=sa.Column(sa.DateTime(timezone=True)),
    )

    auction_id: int | None = Field(
        foreign_key="auction.id", ondelete="CASCADE"
    )
    auction: Auction | None = Relationship(
        sa_relationship=relationship(back_populates="bids")
    )


class BidCreate(SQLModel):
    amount: float
