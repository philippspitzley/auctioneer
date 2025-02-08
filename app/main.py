from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

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
# Welcome to the Auctioneer API! 🚀
#### This API allows you to manage auctions, users, and products.
""",
)


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(auctions.router)
app.include_router(products.router)


@app.get("/", response_class=RedirectResponse)
async def root(request: Request):
    return RedirectResponse(request.url_for("swagger_ui_html"))
