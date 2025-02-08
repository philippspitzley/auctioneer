from fastapi import APIRouter, HTTPException

from .. import db_handler as db
from ..dependencies import AdminRequired, SessionDep, UserRequired
from ..models.filter_model import ProductFilter
from ..models.product_model import Product

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post("/", dependencies=[AdminRequired])
async def create_product(product: Product, session: SessionDep) -> Product:
    return db.add_object(product, session)


@router.get("/", dependencies=[UserRequired], response_model=list[Product])
async def read_products(
    session: SessionDep,
    search_term: str | None = None,
    searched_column: ProductFilter | None = ProductFilter.NAME,
    order_by: ProductFilter | None = ProductFilter.NAME,
    reverse: bool = False,
    offset: int = 0,
    limit: int = 100,
):
    # return session.exec(select(Product)).all()
    return db.read_objects(
        Product,
        session,
        search_term,
        searched_column,
        order_by,
        reverse,
        offset,
        limit,
    )


@router.get("/{product_id}", dependencies=[UserRequired])
async def read_product(product_id: int, session: SessionDep) -> Product:
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    print("HEERE: ", product.auction)
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
