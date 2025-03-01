from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from .. import db_handler as db
from .. import utils
from ..dependencies import SessionDep, UserRequired
from ..models.auction_model import (
    AuctionCreate,
    AuctionCreateFromProduct,
    AuctionPublic,
)
from ..models.filter_model import ProductFilter
from ..models.product_model import Category, Product, ProductCreate
from ..models.user_model import UserPublic
from .auctions import create_auction

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post(
    "/",
    dependencies=[UserRequired],
    tags=["Auction Live Cycle", "Product CRUD"],
)
async def create_product(
    product: ProductCreate, session: SessionDep
) -> Product:
    """
    ## Create a new product

    _Requires admin permissions._

    ### Parameters

    * `product`: `Product` The product representation to create.

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    ### Returns

    * `Product`: The newly created product representation:

    ### Raises

    * `HTTPException`: If the product already exists.
    """
    product_dict = product.model_dump()
    time_stamp = utils.get_current_timestamp()

    new_product = Product(**product_dict, created_at=time_stamp)
    return db.add_object(new_product, session)


@router.get(
    "/{product_id}",
    dependencies=[UserRequired],
    tags=["Product CRUD"],
)
async def read_product(product_id: int, session: SessionDep) -> Product:
    # product = session.get(Product, product_id)
    # if not product:
    #     raise HTTPException(status_code=404, detail="Product not found")
    """
    ## Retrieve a product by ID

    _Requires user authentication._

    ### Parameters

    * `product_id`: `int` The ID of the product to retrieve.

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    ### Returns

    * `Product`: The product representation with the given ID.

    ### Raises

    * `HTTPException`: If the product is not found.
    """
    product = db.read_object(Product, session, product_id)
    return product


@router.get(
    "/",
    dependencies=[UserRequired],
    tags=["Product CRUD"],
)
async def read_products(
    session: SessionDep,
    search_term: str | None = None,
    searched_column: ProductFilter = ProductFilter.NAME,
    order_by: ProductFilter = ProductFilter.NAME,
    reverse: bool = False,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> list[Product]:
    """
    ## Retrieve a list of products

    _Requires user authentication._

    ### Parameters

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    * `search_term`: `str` The search term to filter the products by. The searched column is specified by `searched_column`.

    * `searched_column`: `ProductFilter` The column to search in. Defaults to `ProductFilter.NAME`.

    * `order_by`: `ProductFilter` The column to order the products by. Defaults to `ProductFilter.NAME`.

    * `reverse`: `bool` Whether to reverse the order. Defaults to `False`.

    * `offset`: `int` The offset of the first product to retrieve. Defaults to `0`.

    * `limit`: `int` The maximum number of products to retrieve. Defaults to `10`.

    ### Returns

    * `list[Product]`: A list of product representations:

    ### Raises

    * `HTTPException`: If the query fails.
    """
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


@router.patch(
    "/{product_id}",
    dependencies=[UserRequired],
    tags=["Product CRUD"],
)
async def update_product(
    product_id: int,
    update_data: Product,
    session: SessionDep,
):
    """
    ## Update a product

    _Requires admin permissions._

    ### Parameters

    * `product_id`: `int` The ID of the product to update.

    * `update_data`: `Product` The data to update the product with.

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    ### Returns

    * `Product`: The updated product representation:

    ### Raises

    * `HTTPException`: If the product is not found.
    """
    return db.update_object(product_id, Product, update_data, session)


@router.delete(
    "/{product_id}",
    dependencies=[UserRequired],
    tags=["Product CRUD"],
)
async def delete_product(product_id: int, session: SessionDep):
    """
    ## Delete a product by ID

    _Requires admin permissions._

    ### Parameters

    * `product_id`: `int` The ID of the product to delete.

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    ### Returns

    * `dict[str, bool]`: A dictionary with a single key-value pair, {"ok": True}.

    ### Raises

    * `HTTPException`: If the product is not found.
    """
    db.delete_object(product_id, Product, session)
    return {"ok": True}


###############################################################################
############################## Auction Live Cycle #############################
###############################################################################


@router.post(
    "/{product_id}/create_auction",
    dependencies=[UserRequired],
    tags=["Auction Live Cycle"],
)
async def create_auction_for_product(
    product_id: int,
    session: SessionDep,
    auction: AuctionCreateFromProduct,
) -> AuctionPublic:
    """
    ## Create an auction for a specific product

    _Requires user authentication._

    ### Parameters

    * `product_id`: `int` The ID of the product to create an auction for.

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    * `auction`: `AuctionCreateFromProduct` The auction representation to create.

        * required fields: `starting_price`, `min_bid`, `instant_buy_price`

        * optional fields: `starting_price`, `min_bid`, `instant_buy_price`

    ### Returns

    * `AuctionPublic`: The public auction representation:

    ### Raises

    * `HTTPException`: If the product is not found or the auction is invalid.
    """
    product = db.read_object(Product, session, product_id)
    if product.sold:
        raise HTTPException(
            status_code=400, detail="Product has already been sold"
        )
    auction_dict = auction.model_dump()
    new_auction = AuctionCreate(
        **auction_dict,
        product_id=product_id,
        owner_id=product.owner_id,
    )

    public_auction = await create_auction(new_auction, session)
    return public_auction


###############################################################################
########################### Other Product Endpoints ###########################
###############################################################################


@router.get("/{product_id}/auction", dependencies=[UserRequired])
async def read_product_auction(
    product_id: int, session: SessionDep
) -> AuctionPublic:
    """
    ## Retrieve the auction for a specific product

    _Requires user authentication._

    ### Parameters

    * `product_id`: `int` The ID of the product to retrieve the auction for.

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    ### Returns

    * `AuctionPublic`: The public auction representation associated with the given product ID.

    ### Raises

    * `HTTPException`: If the product or auction is not found.
    """
    product = db.read_object(Product, session, product_id)
    auction = product.auction
    return AuctionPublic.model_validate(auction)


@router.get("/{product_id}/owner", dependencies=[UserRequired])
async def read_product_owner(
    product_id: int, session: SessionDep
) -> UserPublic:
    """
    ## Retrieve the owner of a specific product

    _Requires user authentication._

    ### Parameters

    * `product_id`: `int` The ID of the product to retrieve the owner for.

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    ### Returns

    * `UserPublic`: The public user representation of the product owner.

    ### Raises

    * `HTTPException`: If the product is not found.
    """

    product = db.read_object(Product, session, product_id)
    return UserPublic.model_validate(product.owner)


@router.post("/{product_id}/add_category", dependencies=[UserRequired])
async def add_product_category(
    product_id: int, category: Category, session: SessionDep
) -> Product:
    """
    ## Add a category to a product

    _Requires user authentication._

    ### Parameters

    * `product_id`: `int` The ID of the product to add the category to.

    * `category`: `Category` The category to add to the product.

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    ### Returns

    * `Product`: The updated product representation.

    ### Raises

    * `HTTPException`: If the product is not found.
    """
    product = db.read_object(Product, session, product_id)
    product.categories.append(category)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.get("/{product_id}/categories", dependencies=[UserRequired])
async def read_product_categories(
    product_id: int, session: SessionDep
) -> list[Category]:
    """
    ## Retrieve categories for a specific product

    _Requires user authentication._

    ### Parameters

    * `product_id`: `int` The ID of the product to retrieve categories for.

    * `session`: `SessionDep` The database session used for querying.
        * __Not needed for api calls__.

    ### Returns

    * `list[Category]`: A list of categories associated with the given product ID.

    ### Raises

    * `HTTPException`: If the product is not found.
    """
    product = db.read_object(Product, session, product_id)
    return product.categories
