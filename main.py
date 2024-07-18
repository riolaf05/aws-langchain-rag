from uvicorn import run
from fastapi import FastAPI
from logging import Logger

from api.routers import (
    upload_router,
    process_router,
    embed_router
)

app = FastAPI(
    title="Poc",
    description="Poc",
)

app.include_router(upload_router.router)
app.include_router(process_router.router)
app.include_router(embed_router.router)

if __name__ == "__main__":
    run("main:app", host="0.0.0.0", port=3000, reload=True)
