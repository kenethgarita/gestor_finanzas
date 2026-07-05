from fastapi import FastAPI

from app.db import engine
from app.models import Base
from app.routes import categorias, cuentas, presupuestos, transacciones, usuarios 


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gestor de Finanzas")

app.include_router(usuarios.router)
app.include_router(cuentas.router)
app.include_router(categorias.router)
app.include_router(transacciones.router)
app.include_router(presupuestos.router)


@app.get("/")
def root():
    return {"status": "ok"}