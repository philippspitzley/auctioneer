from enum import Enum


class Filter(str, Enum):
    pass


class AuctionFilter(Filter):
    ID = "id"
    OWNER_ID = "owner_id"
    PRODUCT_ID = "product_id"
    STATE = "state"
    START_TIME = "start_time"
    END_TIME = "end_time"
    STARTING_PRICE = "starting_price"
    MIN_BID = "min_bid"
    INSTANT_BUY_PRICE = "instant_buy_price"
    BUYER_ID = "buyer_id"
    SOLD_PRICE = "sold_price"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class BidFilter(Filter):
    ID = "id"
    AUCTION_ID = "auction_id"
    BIDDER_ID = "bidder_id"
    AMOUNT = "amount"
    CREATED_AT = "created_at"


class ProductFilter(Filter):
    ID = "id"
    NAME = "name"
    DESCRIPTION = "description"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class CategoryFilter(Filter):
    ID = "id"
    NAME = "name"  # type: ignore
    DESCRIPTION = "description"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class UserFilter(Filter):
    ID = "id"
    USERNAME = "username"
    EMAIL = "email"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
