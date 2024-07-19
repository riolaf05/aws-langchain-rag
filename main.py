from uvicorn import run
from fastapi import FastAPI
from logging import Logger

from api.routers import (
    embed_documents_router,
    embed_image_router,
    upload_router,
    process_router,
    stt_router
)

app = FastAPI(
    title="RAG-API",
    description="RAG-API",
)

app.include_router(upload_router.router)
app.include_router(process_router.router)
app.include_router(embed_image_router.router)
app.include_router(embed_documents_router.router)
app.include_router(stt_router.router)

if __name__ == "__main__":
    run("main:app", host="0.0.0.0", port=3000, reload=True)
