from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import Categoria, Cuenta, Transaccion, Usuario
from app.schemas import TransaccionCreate, TransaccionOut, TransaccionUpdate

router = APIRouter(prefix="/transacciones", tags=["Transacciones"])


@router.post("/", response_model=TransaccionOut, status_code=status.HTTP_201_CREATED)
def crear_transaccion(
    transaccion: TransaccionCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    categoria = (
        db.query(Categoria)
        .filter(
            Categoria.id == transaccion.categoria_id,
            Categoria.usuario_id == usuario_actual.id,
        )
        .first()
    )
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")

    if transaccion.cuenta_id is not None:
        cuenta = (
            db.query(Cuenta)
            .filter(
                Cuenta.id == transaccion.cuenta_id,
                Cuenta.usuario_id == usuario_actual.id,
            )
            .first()
        )
        if cuenta is None:
            raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    datos = transaccion.model_dump()
    datos["usuario_id"] = usuario_actual.id
    if datos["fecha"] is None:
        datos["fecha"] = datetime.utcnow()

    db_transaccion = Transaccion(**datos)
    db.add(db_transaccion)
    db.commit()
    db.refresh(db_transaccion)
    return db_transaccion


@router.get("/", response_model=list[TransaccionOut])
def listar_transacciones(
    categoria_id: int | None = None,
    tipo: str | None = None,
    cuenta_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    query = db.query(Transaccion).filter(Transaccion.usuario_id == usuario_actual.id)
    if categoria_id is not None:
        query = query.filter(Transaccion.categoria_id == categoria_id)
    if cuenta_id is not None:
        query = query.filter(Transaccion.cuenta_id == cuenta_id)
    if tipo is not None:
        query = query.filter(Transaccion.tipo == tipo)
    return query.order_by(Transaccion.fecha.desc()).offset(skip).limit(limit).all()


@router.get("/{transaccion_id}", response_model=TransaccionOut)
def obtener_transaccion(
    transaccion_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    db_transaccion = (
        db.query(Transaccion)
        .filter(
            Transaccion.id == transaccion_id,
            Transaccion.usuario_id == usuario_actual.id,
        )
        .first()
    )
    if db_transaccion is None:
        raise HTTPException(status_code=404, detail="Transaccion no encontrada")
    return db_transaccion


@router.patch("/{transaccion_id}", response_model=TransaccionOut)
def actualizar_transaccion(
    transaccion_id: int,
    cambios: TransaccionUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    db_transaccion = (
        db.query(Transaccion)
        .filter(
            Transaccion.id == transaccion_id,
            Transaccion.usuario_id == usuario_actual.id,
        )
        .first()
    )
    if db_transaccion is None:
        raise HTTPException(status_code=404, detail="Transaccion no encontrada")

    datos = cambios.model_dump(exclude_unset=True)

    if "categoria_id" in datos:
        categoria = (
            db.query(Categoria)
            .filter(
                Categoria.id == datos["categoria_id"],
                Categoria.usuario_id == usuario_actual.id,
            )
            .first()
        )
        if categoria is None:
            raise HTTPException(status_code=404, detail="Categoria no encontrada")

    if "cuenta_id" in datos:
        cuenta = (
            db.query(Cuenta)
            .filter(
                Cuenta.id == datos["cuenta_id"],
                Cuenta.usuario_id == usuario_actual.id,
            )
            .first()
        )
        if cuenta is None:
            raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    for campo, valor in datos.items():
        setattr(db_transaccion, campo, valor)

    db.commit()
    db.refresh(db_transaccion)
    return db_transaccion


@router.delete("/{transaccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_transaccion(
    transaccion_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    db_transaccion = (
        db.query(Transaccion)
        .filter(
            Transaccion.id == transaccion_id,
            Transaccion.usuario_id == usuario_actual.id,
        )
        .first()
    )
    if db_transaccion is None:
        raise HTTPException(status_code=404, detail="Transaccion no encontrada")
    db.delete(db_transaccion)
    db.commit()