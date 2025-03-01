import random
from datetime import datetime, timedelta
from decimal import Decimal

import pytz

from app.models.auction_model import Auction, Bid, State
from app.models.product_model import Product
from app.models.user_model import Role, User

tz = pytz.timezone("Europe/Berlin")
date_created_at = datetime(2025, 2, 25, 8, 25, 28, tzinfo=tz)
date_end_time = datetime(2025, 2, 25, 8, 35, 5, tzinfo=tz)
date_bid_at = datetime(2025, 2, 25, 8, 30, 5, tzinfo=tz)


def create_mock_user(user_id: int = 1) -> User:
    return User(
        id=user_id,
        username=f"TestUser{user_id}",
        email=f"user{user_id}@example.com",
        role=Role.user,
        password_hash="fake_hasch_pw",
    )


def create_mock_product(product_id: int = 1, owner_id: int = 1) -> Product:
    return Product(
        id=product_id,
        owner_id=owner_id,
        name=f"Product {product_id}",
        description=f"Description for product {product_id}",
        sold=False,
        created_at=date_created_at,
    )


def create_mock_auction(
    auction_id: int = 1,
    product: Product = None,
    state: State = State.live,  # type: ignore
) -> Auction:
    product = product or create_mock_product(product_id=auction_id)

    random_timedelta = timedelta(
        hours=random.randint(0, 2), minutes=random.randint(0, 59)
    )

    return Auction(
        id=auction_id,
        owner_id=product.owner_id,
        product_id=product.id,
        created_at=date_created_at,
        state=state,
        start_time=datetime.now(tz) - random_timedelta,
        end_time=datetime.now(tz),
        starting_price=Decimal("10"),
        min_bid=Decimal("2"),
        instant_buy=False,
        instant_buy_price=Decimal("100"),
        product=product,
    )


def create_mock_bid(
    bid_id: int = 1, auction_id: int = 1, bidder_id: int = 2
) -> Bid:
    return Bid(
        id=bid_id,
        bidder_id=bidder_id,
        auction_id=auction_id,
        amount=Decimal("100"),
        created_at=date_bid_at,
    )


#####################################


def create_test_product(
    owner_id: int = 1, name: str = "Product", description: str = "Description"
) -> dict:
    return {"owner_id": owner_id, "name": name, "description": description}
