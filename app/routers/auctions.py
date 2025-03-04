import asyncio
from datetime import timedelta
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic import ValidationError
from sqlmodel import Session

from .. import db_handler as db
from .. import utils
from ..config import HOST_URL, JINJA_AUCTION_EMAIL_TEMPLATE, JINJA_ENV
from ..dependencies import AdminRequired, SessionDep, UserRequired
from ..models.auction_model import (
    Auction,
    AuctionCreate,
    AuctionLive,
    AuctionPublic,
    AuctionUpdate,
    Bid,
    BidCreate,
    State,
)
from ..models.filter_model import AuctionFilter
from ..models.product_model import Product
from ..models.user_model import User, UserPublic
from ..services.async_mail import send_email_async

router = APIRouter(prefix="/auctions")


@router.post(
    "/",
    dependencies=[UserRequired],
    tags=["Auction CRUD"],
)
async def create_auction(
    auction: AuctionCreate, session: SessionDep
) -> AuctionPublic:
    """
    ## Create a new auction

    _Requires user permissions._

    ### Parameters

    * `auction`: `AuctionCreate` The auction representation to create.
        * required fields: `owner_id`, `product_id`, starting_price

        * optional fields: `starting_price`, `min_bid`, `instant_buy_price`

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    ### Returns

    * `AuctionPublic`: The public auction representation:

    ### Raises

    * `HTTPException`: If the auction already exists.
    """

    auction_dict = auction.model_dump()
    time_stamp = utils.get_current_timestamp()

    new_auction = Auction(**auction_dict, created_at=time_stamp)
    db_auction = db.add_object(new_auction, session)
    public_auction = AuctionPublic.model_validate(db_auction)
    return public_auction


@router.get(
    "/",
    dependencies=[UserRequired],
    tags=["Auction CRUD"],
)
async def read_auctions(
    session: SessionDep,
    search_term: str | None = None,
    searched_column: AuctionFilter = AuctionFilter.ID,
    order_by: AuctionFilter = AuctionFilter.ID,
    reverse: bool = False,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=0, le=100)] = 10,
) -> list[AuctionPublic]:
    """
    ## Retrieve a list of auctions

    _Requires user authentication._

    ### Parameters

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    * `search_term`: `str` The search term to filter the auctions by. The searched column is specified by `searched_column`.

    * `searched_column`: `AuctionFilter` The column to search in. Defaults to `AuctionFilter.ID`.

    * `order_by`: `AuctionFilter` The column to order the auctions by. Defaults to `AuctionFilter.ID`.

    * `reverse`: `bool` Whether to reverse the order. Defaults to `False`.

    * `offset`: `int` The offset of the first auction to retrieve. Defaults to `0`.

    * `limit`: `int` The maximum number of auctions to retrieve. Defaults to `10`.

    ### Returns

    * `list[AuctionPublic]`: A list of public auction representations:

    ### Raises

    * `HTTPException`: If the query fails.
    """

    auctions = db.read_objects(
        Auction,
        session,
        search_term,
        searched_column,
        order_by,
        reverse,
        offset,
        limit,
    )

    return [AuctionPublic.model_validate(auction) for auction in auctions]


@router.get(
    "/{auction_id}",
    dependencies=[UserRequired],
    tags=["Auction CRUD"],
)
async def read_auction(auction_id: int, session: SessionDep) -> AuctionPublic:
    """
    ## Retrieve an auction by ID

    _Requires user authentication._

    ### Parameters

    * `auction_id`: `int` The ID of the auction to retrieve.

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    ### Returns

    * `AuctionPublic`: The public auction representation:

    ### Raises

    * `HTTPException`: If the auction is not found.
    """
    auction = db.read_object(Auction, session, auction_id)
    return AuctionPublic.model_validate(auction)


@router.patch(
    "/{auction_id}",
    dependencies=[AdminRequired],
    tags=["Auction CRUD"],
)
async def update_auction(
    auction_id: int, update_data: AuctionUpdate, session: SessionDep
):
    """
    ## Update an auction

    _Requires admin permissions._

    ### Parameters

    * `auction_id`: `int` The ID of the auction to update.

    * `update_data`: `AuctionUpdate` The data to update the auction with.

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    ### Returns

    * `AuctionPublic`: The updated public auction representation:

    ### Raises

    * `HTTPException`: If the auction is not found or update fails.
    """

    updated_auction = db.update_object(
        auction_id, Auction, update_data, session
    )
    return AuctionPublic.model_validate(updated_auction)


@router.delete(
    "/{auction_id}",
    dependencies=[UserRequired],
    tags=["Auction CRUD"],
)
async def delete_auction(
    auction_id: int, session: SessionDep
) -> dict[str, bool]:
    """
    ## Delete an auction

    _Requires either user or admin permissions._

    ### Parameters

    * `auction_id`: `int` The ID of the auction to delete.

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    ### Returns

    * `dict[str, bool]`: A dictionary with a single key-value pair, {"ok": True}.

    ### Raises

    * `HTTPException`: If the auction is not found.
    """

    db.delete_object(auction_id, Auction, session)
    return {"ok": True}


################################################################################
############################## Auction Live Cycle ##############################
################################################################################


@router.post(
    "/{auction_id}/publish",
    dependencies=[UserRequired],
    tags=["Auction Live Cycle"],
)
async def start_auction(
    auction_id: int,
    session: SessionDep,
    duration: timedelta = timedelta(minutes=5),
):
    """
    ## Start an auction

    _Requires user authentication._

    ### Parameters

    * `auction_id`: `int` The ID of the auction to start.

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    * `duration`: `timedelta` The duration of the auction. Defaults to 5 minutes.
        * example: "PT5M" = 5 minutes, "PT1H" = 1 hour, "PT1H30M" = 1 hour and 30 minutes

    ### Returns

    * `dict[str, bool]`: A dictionary with a single key-value pair, {"ok": True}.

    ### Raises

    * `HTTPException`: If the auction is not found or is not in {State.setup} state.
    """

    db_auction = db.read_object(Auction, session, auction_id)

    if db_auction.state != State.setup:
        raise HTTPException(
            status_code=400,
            detail=f"Auction with id {auction_id} is in {db_auction.state} state. Only auctions in {State.setup} state can be published.",
        )

    db_auction.state = State.live
    current_time = utils.get_current_timestamp()
    db_auction.end_time = current_time + duration
    db_auction.start_time = current_time
    db_auction.updated_at = current_time
    session.add(db_auction)
    session.commit()
    session.refresh(db_auction)

    return {"ok": True}


@router.post(
    "/{auction_id}/bid",
    dependencies=[UserRequired],
    tags=["Auction Live Cycle"],
)
async def bid_on_auction(
    auction_id: int,
    current_user: Annotated[User, UserRequired],
    bid: BidCreate,
    session: SessionDep,
) -> dict[str, bool | Bid]:
    """
    ## Bid on an auction

    _Requires user authentication._

    ### Parameters

    * `auction_id`: `int` The ID of the auction to bid on.

    * `current_user`: `Annotated[User, UserRequired]` The current user.

    * `bid`: `BidCreate` The bid to place on the auction.

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    ### Returns

    * `Bid`: The newly created bid.

    ### Raises

    * `HTTPException`: If the auction is not found or is not in {State.live} state.
    """

    # TODO: current_user.id check should not happen because is already checked in UserRequired, but implemented it for IDE purposes
    if not current_user.id:
        raise HTTPException(status_code=400, detail="User ID not found")

    db_auction = db.read_object(Auction, session, auction_id)

    # check if auction is live
    if db_auction.has_ended() or db_auction.state == State.setup:
        end_time = db_auction.end_time if db_auction.end_time else None
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"You cannot bid on auction {auction_id}.",
                "state": db_auction.state,
                "ended": end_time < utils.get_current_timestamp()
                if end_time
                else False,
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S")
                if end_time
                else None,
                "instant_buy": db_auction.instant_buy,
            },
        )

    # end auction early if instant buy
    if (
        db_auction.instant_buy_price
        and bid.amount >= db_auction.instant_buy_price
    ):
        new_bid = create_bid(
            auction_id, current_user.id, bid, session, db_auction
        )
        new_bid.amount = db_auction.instant_buy_price
        db_auction.instant_buy = True
        db_auction.product.sold = True
        db_auction.end_time = new_bid.created_at
        session.commit()
        session.refresh(new_bid)
        return {"bid": new_bid, "instant_buy": True}

    # check for highest bidder
    highest_bidder = db_auction.get_highest_bid()
    live_auction = AuctionLive.model_validate(db_auction)

    # check for min bid
    min_bid = db_auction.min_bid if db_auction.min_bid else Decimal("0.01")

    # check for highest bid
    current_highest_bid = (
        highest_bidder.amount if highest_bidder else Decimal("0")
    )

    # check if bid is too low
    bid_too_low = is_bid_too_low(
        bid.amount, current_highest_bid, live_auction, min_bid
    )
    if bid_too_low:
        min_required_bid = calculate_min_required_bid(
            live_auction, current_highest_bid, min_bid
        )

        # Raise the HTTPException with the calculated message
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Bid is too low.",
                "bid": float(bid.amount),
                "min_required_bid": float(min_required_bid),
                "starting_price": float(live_auction.starting_price),
                "min_bid": float(min_bid),
                "highest_bid": float(current_highest_bid),
            },
        )

    # create new bid
    new_bid = create_bid(auction_id, current_user.id, bid, session, db_auction)
    return {"bid": new_bid, "instant_buy": False}


def calculate_min_required_bid(live_auction, current_highest_bid, min_bid):
    """Calculate the minimum required bid."""
    if current_highest_bid == 0 and live_auction.starting_price == 0:
        return live_auction.starting_price + min_bid
    return max(live_auction.starting_price, current_highest_bid + min_bid)


def is_bid_too_low(bid_amount, current_highest_bid, live_auction, min_bid):
    """Check if the bid is below starting price or minimum increment."""
    # Case 1: Bid is below starting price
    if current_highest_bid == 0 and bid_amount < live_auction.starting_price:
        return True

    # Case 2: Bid is below the minimum increment
    if current_highest_bid > 0 and bid_amount < current_highest_bid + min_bid:
        return True

    return False


def create_bid(
    auction_id: int,
    current_user_id: int,
    bid: BidCreate,
    session: Session,
    db_auction: Auction,
):
    bid_dict = bid.model_dump()
    new_bid = Bid(
        **bid_dict,
        bidder_id=current_user_id,
        auction_id=auction_id,
        created_at=utils.get_current_timestamp(),
    )

    db_auction.bids.append(new_bid)
    # session.add(db_auction)
    session.add(new_bid)
    session.commit()
    # session.refresh(db_auction)
    session.refresh(new_bid)
    return new_bid


@router.get(
    "/{auction_id}/bids",
    dependencies=[UserRequired],
    tags=["Auction Live Cycle"],
)
async def read_auction_bids(
    auction_id: int,
    session: SessionDep,
):
    """
    ## Retrieve all bids for a specific auction

    _Requires user authentication._

    ### Parameters

    * `auction_id`: `int` The ID of the auction to retrieve bids for.

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    ### Returns

    * `list[Bid]`: A list of bids associated with the given auction ID.

    ### Raises

    * `HTTPException`: If the auction is not found.
    """

    db_auction = db.read_object(Auction, session, auction_id)
    return db_auction.bids


@router.get(
    "/{auction_id}/highest_bidder",
    dependencies=[UserRequired],
    tags=["Auction Live Cycle"],
)
async def get_highest_bidder(
    auction_id: int,
    session: SessionDep,
):
    """
    ## Retrieve the highest bidder for a specific auction

    _Requires user authentication._

    ### Parameters

    * `auction_id`: `int` The ID of the auction to retrieve the highest bidder for.

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    ### Returns

    * `UserPublic`: The highest bidder associated with the given auction ID.

    ### Raises

    * `HTTPException`: If no bids are found for the auction.
    """

    db_auction = db.read_object(Auction, session, auction_id)
    highest_bidder = db_auction.get_highest_bid()
    if not highest_bidder:
        raise HTTPException(status_code=400, detail="No bids found")
    return highest_bidder


@router.get("/finished_auctions/", tags=["Auction Live Cycle"])
def get_finished_auctions(session: SessionDep) -> list[AuctionPublic]:
    """
    ## Retrieve a list of finished auctions

    _Requires user authentication._

    ### Parameters

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    ### Returns

    * `list[AuctionPublic]`: A list of public auction representations for auctions that have finished, ordered by end time in descending order.

    ### Raises

    * `HTTPException`: If the query fails.
    """

    auctions = db.read_objects(
        Auction,
        session,
        search_term=State.finished,
        searched_column=AuctionFilter.STATE,
        order_by=AuctionFilter.END_TIME,
        reverse=True,
    )
    return [AuctionPublic.model_validate(auction) for auction in auctions]


###############################################################################
################################ Linked Objects ###############################
###############################################################################


@router.get(
    "/{auction_id}/product",
    dependencies=[UserRequired],
    tags=["Auction Relations"],
)
async def read_auction_product(
    auction_id: int, session: SessionDep
) -> Product:
    """
    ## Retrieve the product for a specific auction

    _Requires user authentication._

    ### Parameters

    * `auction_id`: `int` The ID of the auction to retrieve the product for.

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    ### Returns

    * `Product`: The product representation associated with the given auction ID.

    ### Raises

    * `HTTPException`: If the auction or product is not found.
    """
    auction = db.read_object(Auction, session, auction_id)
    product = auction.product
    if product is None:
        raise HTTPException(status_code=400, detail="No product found")
    return Product.model_validate(product)


@router.get(
    "/{auction_id}/owner",
    dependencies=[UserRequired],
    tags=["Auction Relations"],
)
async def read_auction_owner(
    auction_id: int, session: SessionDep
) -> UserPublic:
    """
    ## Retrieve the owner for a specific auction

    _Requires user authentication._

    ### Parameters

    * `auction_id`: `int` The ID of the auction to retrieve the product for.

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    ### Returns

    * `UserPublic`: The public user representation associated with the given auction ID.

    ### Raises

    * `HTTPException`: If the auction or owner is not found.
    """
    auction = db.read_object(Auction, session, auction_id)
    owner = auction.owner
    if owner is None:
        raise HTTPException(status_code=400, detail="No owner found")
    return UserPublic.model_validate(owner)


@router.get(
    "/{auction_id}/buyer",
    dependencies=[UserRequired],
    tags=["Auction Relations"],
)
async def read_auction_buyer(
    auction_id: int, session: SessionDep
) -> UserPublic:
    """
    ## Retrieve the owner for a specific auction

    _Requires user authentication._

    ### Parameters

    * `auction_id`: `int` The ID of the auction to retrieve the product for.

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    ### Returns

    * `UserPublic`: The public user representation associated with the given auction ID.

    ### Raises

    * `HTTPException`: If the auction or owner is not found.
    """
    auction = db.read_object(Auction, session, auction_id)
    buyer = auction.buyer
    if buyer is None:
        raise HTTPException(status_code=400, detail="No buyer found")
    return UserPublic.model_validate(buyer)


################################################################################
############################### Process Functions ##############################
################################################################################


def process_finished_auctions(session: Session):
    """
    Processes all live auctions and marks them as finished if their end time has passed.
    It also sends notification emails to the auction owner and the highest bidder if applicable.

    :param session: The database session used for querying and updating auctions.
    :type session: Session

    :raises HTTPException: If there are no live auctions to process. To not interrupt the process, the function logs a message and returns.

    The function performs the following actions:

    - Retrieves all live auctions from the database.
    - Checks each auction's end time against the current time.
    - If the auction has ended:
      - Determines the highest bidder and updates the auction's buyer and sold status.
      - Marks the auction as finished.
      - Sends an email notification to the auction owner.
      - Sends an email notification to the highest bidder if there is one.
    - Commits changes to the database.
    - Logs the number of auctions processed.
    """

    try:
        all_live_auctions = db.read_objects(
            Auction,
            session,
            search_term=State.live,
            searched_column=AuctionFilter.STATE,
            order_by=AuctionFilter.END_TIME,
            reverse=True,
        )
    except HTTPException:
        return

    finished_auctions = []

    for auction in all_live_auctions:
        if not auction.end_time:
            utils.pretty_print(
                "....",
                f"Auction with id {auction.id} has no end_time, resetting state back to setup",
            )
            auction.state = State.setup
            continue

        current_time = utils.get_current_timestamp()

        if auction.end_time < current_time or auction.instant_buy:
            finish_auction(auction, session)
            finished_auctions.append(auction.id)

    if finished_auctions:
        utils.pretty_print(
            "....",
            f"Finished {len(finished_auctions)} auctions: {finished_auctions}",
        )

    return finished_auctions


def finish_auction(auction: Auction, session: Session) -> Auction:
    highest_bid = auction.get_highest_bid()
    owner = UserPublic.model_validate(auction.owner)
    try:
        buyer = UserPublic.model_validate(auction.buyer)
    except ValidationError:
        buyer = None

    if highest_bid and highest_bid.amount > 0:
        auction.buyer_id = highest_bid.bidder_id
        auction.sold_price = highest_bid.amount
        auction.updated_at = utils.get_current_timestamp()
        auction.product.sold = True

    auction.state = State.finished

    session.add(auction)
    session.commit()
    session.refresh(auction)

    # send emails
    asyncio.run(send_auction_email(auction, owner))

    if buyer:
        asyncio.run(send_auction_email(auction, buyer))

    return auction


async def send_auction_email(auction: Auction, receiver: UserPublic):
    # Render email template
    template = JINJA_ENV.get_template(JINJA_AUCTION_EMAIL_TEMPLATE)

    auction_endpoint = f"auctions/?search_term={auction.id}&searched_column=id&order_by=id&reverse=false&offset=0&limit=1'"
    CREATE_NEW_AUCTION_ENDPOINT = "Auction%20Live%20Cycle/create_auction_for_product_products__product_id__create_auction_post"

    html_content = template.render(
        auction=auction,
        user=receiver,
        product=auction.product,
        auction_link=HOST_URL + auction_endpoint,
        create_new_auction_link=HOST_URL + CREATE_NEW_AUCTION_ENDPOINT,
    )

    email = receiver.email
    subject = f"Auction with {auction.product.name} finished!"
    body = html_content

    await send_email_async(email, subject, body)
