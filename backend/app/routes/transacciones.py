from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Categoria, Transaccion, Usuario
from app.schemas import TransaccionCreate, TransaccionOut, TransaccionUpdate

router = APIRouter(prefix="/transacciones", tags=["Transacciones"])


@router.post("/", response_model=TransaccionOut, status_code=status.HTTP_201_CREATED)
def crear_transaccion(transaccion: TransaccionCreate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == transaccion.usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    categoria = (
        db.query(Categoria).filter(Categoria.id == transaccion.categoria_id).first()
    )
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")

    datos = transaccion.model_dump()
    if datos["fecha"] is None:
        datos["fecha"] = datetime.utcnow()

    db_transaccion = Transaccion(**datos)
    db.add(db_transaccion)
    db.commit()
    db.refresh(db_transaccion)
    return db_transaccion


@router.get("/", response_model=list[TransaccionOut])
def listar_transacciones(
    usuario_id: int | None = None,
    categoria_id: int | None = None,
    tipo: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Transaccion)
    if usuario_id is not None:
        query = query.filter(Transaccion.usuario_id == usuario_id)
    if categoria_id is not None:
        query = query.filter(Transaccion.categoria_id == categoria_id)
    if tipo is not None:
        query = query.filter(Transaccion.tipo == tipo)
    return query.order_by(Transaccion.fecha.desc()).offset(skip).limit(limit).all()


@router.get("/{transaccion_id}", response_model=TransaccionOut)
def obtener_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    db_transaccion = (
        db.query(Transaccion).filter(Transaccion.id == transaccion_id).first()
    )
    if db_transaccion is None:
        raise HTTPException(status_code=404, detail="Transaccion no encontrada")
    return db_transaccion


@router.patch("/{transaccion_id}", response_model=TransaccionOut)
def actualizar_transaccion(
    transaccion_id: int, cambios: TransaccionUpdate, db: Session = Depends(get_db)
):
    db_transaccion = (
        db.query(Transaccion).filter(Transaccion.id == transaccion_id).first()
    )
    if db_transaccion is None:
        raise HTTPException(status_code=404, detail="Transaccion no encontrada")

    datos = cambios.model_dump(exclude_unset=True)

    if "categoria_id" in datos:
        categoria = (
            db.query(Categoria).filter(Categoria.id == datos["categoria_id"]).first()
        )
        if categoria is None:
            raise HTTPException(status_code=404, detail="Categoria no encontrada")

    for campo, valor in datos.items():
        setattr(db_transaccion, campo, valor)

    db.commit()
    db.refresh(db_transaccion)
    return db_transaccion


@router.delete("/{transaccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    db_transaccion = (
        db.query(Transaccion).filter(Transaccion.id == transaccion_id).first()
    )
    if db_transaccion is None:
        raise HTTPException(status_code=404, detail="Transaccion no encontrada")
    db.delete(db_transaccion)
    db.commit()