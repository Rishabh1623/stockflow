from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.services.exceptions import InsufficientStockError, InvalidTransitionError, NotFoundError

app = FastAPI(title="StockFlow API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(InvalidTransitionError)
async def invalid_transition_handler(request: Request, exc: InvalidTransitionError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(InsufficientStockError)
async def insufficient_stock_handler(request: Request, exc: InsufficientStockError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})
