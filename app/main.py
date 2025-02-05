from contextlib import asynccontextmanager

from fastapi import FastAPI

from .routers import auctions, auth, products, users
# from .create_admin import create_admin_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create_admin_user()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Auctioneer API",
    summary="like on the bazar",
    description="""
                ChimichangApp API helps you do awesome stuff. 🚀

                ## Items

                You can **read items**.

                ## Users

                You will be able to:

                * **Create users** (_not implemented_).
                * **Read users** (_not implemented_).

                """,
)


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(auctions.router)
app.include_router(products.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
