from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ORIGINS = [
    "http://localhost:8000",
    "https://localhost:8000",
    "http://127.0.0.1:8000",
    "https://127.0.0.1:8000",
]

METHODS = ["*"]

HEADERS = ["*"]


def register_cors_middlware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINS,
        allow_credentials=True,
        allow_methods=METHODS,
        allow_headers=HEADERS,
    )
