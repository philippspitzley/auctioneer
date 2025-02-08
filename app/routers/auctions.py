from typing import Annotated

from fastapi import APIRouter, Query

from .. import db_handler as db
from ..dependencies import AdminRequired, SessionDep, UserRequired
from ..models.auction_model import (
    Auction,
    AuctionPublic,
)
from ..models.filter_model import AuctionFilter

router = APIRouter(
    prefix="/auctions",
    tags=["Auction"],
)


@router.post("/", dependencies=[AdminRequired])
async def create_auction(
    auction: Auction, session: SessionDep
) -> AuctionPublic:
    db.add_object(auction, session)
    public_user = AuctionPublic.model_validate(auction)
    return public_user


@router.get("/", dependencies=[UserRequired])
async def read_auctions(
    session: SessionDep,
    search_term: str | None = None,
    searched_column: AuctionFilter | None = AuctionFilter.ID,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    order_by: AuctionFilter = AuctionFilter.ID,
    reverse: bool = False,
):
    # stmt = select(Auction).offset(offset).limit(limit).order_by(order_by)
    # auctions = session.exec(stmt).all()

    auctions = db.read_objects(
        Auction,
        session,
        offset=offset,
        limit=limit,
        order_by=order_by,
        reverse=reverse,
    )

    public_auctions = [
        AuctionPublic.model_validate(auction) for auction in auctions
    ]
    return public_auctions


@router.get("/{auction_id}", dependencies=[UserRequired])
async def read_auction(auction_id: int, session: SessionDep) -> AuctionPublic:
    # auction = session.get(Auction, auction_id)
    # if not auction:
    #     raise HTTPException(status_code=404, detail="Auction not found")

    auction = db.read_object(Auction, session, auction_id)
    public_auction = AuctionPublic.model_validate(auction)
    return public_auction


@router.delete("/{auction_id}", dependencies=[AdminRequired])
async def delete_auction(
    auction_id: int, session: SessionDep
) -> dict[str, bool]:
    db.delete_object(auction_id, Auction, session)
    return {"ok": True}
