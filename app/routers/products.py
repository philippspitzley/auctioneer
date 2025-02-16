from typing import Annotated

from fastapi import APIRouter, Query

from .. import db_handler as db
from ..dependencies import AdminRequired, SessionDep, UserRequired
from ..models.auction_model import (
    AuctionCreate,
    AuctionCreateFromProduct,
    AuctionPublic,
)
from ..models.filter_model import ProductFilter
from ..models.product_model import Category, Product
from ..models.user_model import UserPublic
from .auctions import create_auction

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post("/", dependencies=[AdminRequired])
async def create_product(product: Product, session: SessionDep) -> Product:
    return db.add_object(product, session)


@router.post(
    "/{product_id}/create_auction",
    dependencies=[UserRequired],
    tags=["Auction"],
)
async def create_auction_for_product(
    product_id: int,
    session: SessionDep,
    auction: AuctionCreateFromProduct,
) -> AuctionPublic:
    product = db.read_object(Product, session, product_id)
    auction_dict = auction.model_dump()
    new_auction = AuctionCreate(
        **auction_dict,
        product_id=product_id,
        owner_id=product.owner_id,
    )

    public_auction = await create_auction(new_auction, session)
    return public_auction


@router.get("/", dependencies=[UserRequired])
async def read_products(
    session: SessionDep,
    search_term: str | None = None,
    searched_column: ProductFilter = ProductFilter.NAME,
    order_by: ProductFilter = ProductFilter.NAME,
    reverse: bool = False,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> list[Product]:
    products = db.read_objects(
        Product,
        session,
        search_term,
        searched_column,
        order_by,
        reverse,
        offset,
        limit,
    )

    return [Product.model_validate(product) for product in products]


@router.get("/{product_id}", dependencies=[UserRequired])
async def read_product(product_id: int, session: SessionDep) -> Product:
    # product = session.get(Product, product_id)
    # if not product:
    #     raise HTTPException(status_code=404, detail="Product not found")
    product = db.read_object(Product, session, product_id)
    return product


@router.get("/{product_id}/auction", dependencies=[UserRequired])
async def read_product_auction(
    product_id: int, session: SessionDep
) -> AuctionPublic:
    product = db.read_object(Product, session, product_id)
    auction = product.auction
    return AuctionPublic.model_validate(auction)


@router.get("/{product_id}/categories", dependencies=[UserRequired])
async def read_product_categories(
    product_id: int, session: SessionDep
) -> list[Category]:
    product = db.read_object(Product, session, product_id)
    return product.categories


@router.get("/{product_id}/owner", dependencies=[UserRequired])
async def read_product_owner(
    product_id: int, session: SessionDep
) -> UserPublic:
    product = db.read_object(Product, session, product_id)
    return UserPublic.model_validate(product.owner)


@router.post("/{product_id}/add_category", dependencies=[UserRequired])
async def add_product_category(
    product_id: int, category: Category, session: SessionDep
) -> Product:
    product = db.read_object(Product, session, product_id)
    product.categories.append(category)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.patch("/{product_id}", dependencies=[AdminRequired])
async def update_product(
    product_id: int,
    update_data: Product,
    session: SessionDep,
):
    return db.update_object(product_id, Product, update_data, session)


@router.delete("/{product_id}", dependencies=[AdminRequired])
async def delete_product(product_id: int, session: SessionDep):
    db.delete_object(product_id, Product, session)
    return {"ok": True}
