import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import ensure_schema, engine
from app.models import Base
from app.routes import categorias, cuentas, presupuestos, transacciones, usuarios

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

ensure_schema()

app = FastAPI(title="Gestor de Finanzas")

origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5173,http://localhost:5500,http://127.0.0.1:5500"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios.router)
app.include_router(cuentas.router)
app.include_router(categorias.router)
app.include_router(transacciones.router)
app.include_router(presupuestos.router)


@app.get("/")
def root():
    return {"status": "ok"}