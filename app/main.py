from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import create_db_and_tables
from .routers import auth, users

# from .dependencies import get_query_token, get_token_header
# from .routers import auctions, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    print("Shutdown")


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


@app.get("/")
async def root():
    return {"message": "Hello World"}
