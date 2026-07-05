from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Categoria, Presupuesto, Usuario
from app.schemas import PresupuestoCreate, PresupuestoOut, PresupuestoUpdate

router = APIRouter(prefix="/presupuestos", tags=["Presupuestos"])


@router.post("/", response_model=PresupuestoOut, status_code=status.HTTP_201_CREATED)
def crear_presupuesto(presupuesto: PresupuestoCreate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == presupuesto.usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    categoria = (
        db.query(Categoria).filter(Categoria.id == presupuesto.categoria_id).first()
    )
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")

    db_presupuesto = Presupuesto(**presupuesto.model_dump())
    db.add(db_presupuesto)
    db.commit()
    db.refresh(db_presupuesto)
    return db_presupuesto


@router.get("/", response_model=list[PresupuestoOut])
def listar_presupuestos(
    usuario_id: int | None = None,
    categoria_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Presupuesto)
    if usuario_id is not None:
        query = query.filter(Presupuesto.usuario_id == usuario_id)
    if categoria_id is not None:
        query = query.filter(Presupuesto.categoria_id == categoria_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{presupuesto_id}", response_model=PresupuestoOut)
def obtener_presupuesto(presupuesto_id: int, db: Session = Depends(get_db)):
    db_presupuesto = (
        db.query(Presupuesto).filter(Presupuesto.id == presupuesto_id).first()
    )
    if db_presupuesto is None:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    return db_presupuesto


@router.patch("/{presupuesto_id}", response_model=PresupuestoOut)
def actualizar_presupuesto(
    presupuesto_id: int, cambios: PresupuestoUpdate, db: Session = Depends(get_db)
):
    db_presupuesto = (
        db.query(Presupuesto).filter(Presupuesto.id == presupuesto_id).first()
    )
    if db_presupuesto is None:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")

    datos = cambios.model_dump(exclude_unset=True)

    if "categoria_id" in datos:
        categoria = (
            db.query(Categoria).filter(Categoria.id == datos["categoria_id"]).first()
        )
        if categoria is None:
            raise HTTPException(status_code=404, detail="Categoria no encontrada")

    for campo, valor in datos.items():
        setattr(db_presupuesto, campo, valor)

    db.commit()
    db.refresh(db_presupuesto)
    return db_presupuesto


@router.delete("/{presupuesto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_presupuesto(presupuesto_id: int, db: Session = Depends(get_db)):
    db_presupuesto = (
        db.query(Presupuesto).filter(Presupuesto.id == presupuesto_id).first()
    )
    if db_presupuesto is None:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    db.delete(db_presupuesto)
    db.commit()