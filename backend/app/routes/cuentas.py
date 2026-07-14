from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import Cuenta, Usuario
from app.schemas import CuentaCreate, CuentaOut, CuentaUpdate

router = APIRouter(prefix="/cuentas", tags=["Cuentas"])


@router.post("/", response_model=CuentaOut, status_code=status.HTTP_201_CREATED)
def crear_cuenta(
    cuenta: CuentaCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    db_cuenta = Cuenta(
        nombre=cuenta.nombre,
        saldo=cuenta.saldo,
        usuario_id=usuario_actual.id,
    )
    db.add(db_cuenta)
    db.commit()
    db.refresh(db_cuenta)
    return db_cuenta


@router.get("/", response_model=list[CuentaOut])
def listar_cuentas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    return (
        db.query(Cuenta)
        .filter(Cuenta.usuario_id == usuario_actual.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{cuenta_id}", response_model=CuentaOut)
def obtener_cuenta(
    cuenta_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    db_cuenta = (
        db.query(Cuenta)
        .filter(Cuenta.id == cuenta_id, Cuenta.usuario_id == usuario_actual.id)
        .first()
    )
    if db_cuenta is None:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return db_cuenta


@router.patch("/{cuenta_id}", response_model=CuentaOut)
def actualizar_cuenta(
    cuenta_id: int,
    cambios: CuentaUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    db_cuenta = (
        db.query(Cuenta)
        .filter(Cuenta.id == cuenta_id, Cuenta.usuario_id == usuario_actual.id)
        .first()
    )
    if db_cuenta is None:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    for campo, valor in cambios.model_dump(exclude_unset=True).items():
        setattr(db_cuenta, campo, valor)

    db.commit()
    db.refresh(db_cuenta)
    return db_cuenta


@router.delete("/{cuenta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cuenta(
    cuenta_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    db_cuenta = (
        db.query(Cuenta)
        .filter(Cuenta.id == cuenta_id, Cuenta.usuario_id == usuario_actual.id)
        .first()
    )
    if db_cuenta is None:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    db.delete(db_cuenta)
    db.commit()