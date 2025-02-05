from enum import Enum


from fastapi import APIRouter, HTTPException
from sqlmodel import select

from ..utils.helper import get_current_timestamp

from ..dependencies import AdminRequired, SessionDep, UserRequired

from ..models.product_model import Product

from ..db_handler import create_object, delete_object

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


class ProductFilter(str, Enum):
    id = "id"
    name = "name"  # type: ignore # TODO: wtf is this?
    description = "description"


@router.post("/", dependencies=[AdminRequired])
async def create_product(product: Product, session: SessionDep) -> Product:
    return create_object(product, session)


@router.get("/", dependencies=[UserRequired], response_model=list[Product])
async def read_products(session: SessionDep):
    return session.exec(select(Product)).all()


@router.get("/{product_id}", dependencies=[UserRequired])
async def read_product(product_id: int, session: SessionDep) -> Product:
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


router.patch("/{product_id}", dependencies=[AdminRequired])


async def update_product(
    product_id: int, update_data: Product, session: SessionDep
):
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    product_data = update_data.model_dump(exclude_unset=True)

    product_data["updated_at"] = get_current_timestamp()

    db_product.sqlmodel_update(product_data)


@router.delete("/{product_id}", dependencies=[AdminRequired])
async def delete_product(product_id: int, session: SessionDep):
    delete_object(product_id, Product, session)
    return {"ok": True}


@router.get(
    "/search/", dependencies=[UserRequired], response_model=list[Product]
)
async def search_auctions(
    session: SessionDep,
    column_name: ProductFilter,
    search_term: str,
):
    column = getattr(Product, column_name)
    stmt = select(Product).where(column.ilike(f"%{search_term}%"))
    result = session.exec(stmt).all()
    return result
