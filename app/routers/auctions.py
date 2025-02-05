from typing import Annotated


from fastapi import APIRouter, Query
from sqlmodel import select

from ..dependencies import AdminRequired, SessionDep, UserRequired
from ..models.auction_model import (
    Auction,
    AuctionPublic,
    AuctionFilter,
)

router = APIRouter(
    prefix="/auctions",
    tags=["Auction"],
)


@router.post("/", dependencies=[AdminRequired])
async def create_auction(
    auction: Auction, session: SessionDep
) -> AuctionPublic:
    session.add(auction)
    session.commit()
    session.refresh(auction)
    public_user = AuctionPublic.model_validate(auction)
    return public_user


@router.get("/", dependencies=[UserRequired])
async def read_auctions(
    session: SessionDep,
    offset: Annotated[
        int,
        Query(
            ge=0,
            description="Offset of the first shown auction",
        ),
    ] = 0,
    limit: Annotated[
        int,
        Query(
            le=100,
            description="Maximum number of auctions",
        ),
    ] = 10,
    order: Annotated[
        AuctionFilter,
        Query(
            description="Sorting order",
        ),
    ] = AuctionFilter.id,
) -> list[AuctionPublic]:
    stmt = select(Auction).offset(offset).limit(limit).order_by(order)
    auctions = session.exec(stmt).all()
    public_auctions = [
        AuctionPublic.model_validate(auction) for auction in auctions
    ]
    return public_auctions
