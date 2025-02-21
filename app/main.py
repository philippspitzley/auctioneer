from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from .routers import auctions, auth, products, users
from .tasks import scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(
    lifespan=lifespan,
    title="🚀 Auction Platform Interface 🚀",
    description="""###  sell or buy your stuff""",
)

app.include_router(auctions.router)
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(users.router)


# Hidden Routes
@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def root(request: Request):
    return RedirectResponse(request.url_for("swagger_ui_html"))


@app.get("/fake_login", include_in_schema=False)
async def fake_login():
    return {"message": "Hello this is a fake login dummy"}
