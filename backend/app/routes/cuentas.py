from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Cuenta, Usuario
from app.schemas import CuentaCreate, CuentaOut, CuentaUpdate

router = APIRouter(prefix="/cuentas", tags=["Cuentas"])


@router.post("/", response_model=CuentaOut, status_code=status.HTTP_201_CREATED)
def crear_cuenta(cuenta: CuentaCreate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == cuenta.usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db_cuenta = Cuenta(**cuenta.model_dump())
    db.add(db_cuenta)
    db.commit()
    db.refresh(db_cuenta)
    return db_cuenta


@router.get("/", response_model=list[CuentaOut])
def listar_cuentas(
    usuario_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Cuenta)
    if usuario_id is not None:
        query = query.filter(Cuenta.usuario_id == usuario_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{cuenta_id}", response_model=CuentaOut)
def obtener_cuenta(cuenta_id: int, db: Session = Depends(get_db)):
    db_cuenta = db.query(Cuenta).filter(Cuenta.id == cuenta_id).first()
    if db_cuenta is None:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return db_cuenta


@router.patch("/{cuenta_id}", response_model=CuentaOut)
def actualizar_cuenta(
    cuenta_id: int, cambios: CuentaUpdate, db: Session = Depends(get_db)
):
    db_cuenta = db.query(Cuenta).filter(Cuenta.id == cuenta_id).first()
    if db_cuenta is None:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    for campo, valor in cambios.model_dump(exclude_unset=True).items():
        setattr(db_cuenta, campo, valor)

    db.commit()
    db.refresh(db_cuenta)
    return db_cuenta


@router.delete("/{cuenta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cuenta(cuenta_id: int, db: Session = Depends(get_db)):
    db_cuenta = db.query(Cuenta).filter(Cuenta.id == cuenta_id).first()
    if db_cuenta is None:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    db.delete(db_cuenta)
    db.commit()