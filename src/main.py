from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.core.database import client as db_client

from src.middlewares.cors_middleware import register_cors_middlware

from src.routers.documents import router as documents_router
from src.routers.models import router as models_router
from src.routers.auth import router as auth_router
from src.routers.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

    db_client.close()


app = FastAPI(
    title="CortexFlow",
    version="0.0.1",
    lifespan=lifespan
)

register_cors_middlware(app=app)

app.include_router(documents_router)
app.include_router(models_router)
app.include_router(auth_router)
app.include_router(chat_router)


@app.get("/")
def home():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
