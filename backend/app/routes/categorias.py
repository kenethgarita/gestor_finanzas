from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Categoria, Usuario
from app.schemas import CategoriaCreate, CategoriaOut, CategoriaUpdate

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.post("/", response_model=CategoriaOut, status_code=status.HTTP_201_CREATED)
def crear_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == categoria.usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db_categoria = Categoria(**categoria.model_dump())
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria


@router.get("/", response_model=list[CategoriaOut])
def listar_categorias(
    usuario_id: int | None = None,
    tipo: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Categoria)
    if usuario_id is not None:
        query = query.filter(Categoria.usuario_id == usuario_id)
    if tipo is not None:
        query = query.filter(Categoria.tipo == tipo)
    return query.offset(skip).limit(limit).all()


@router.get("/{categoria_id}", response_model=CategoriaOut)
def obtener_categoria(categoria_id: int, db: Session = Depends(get_db)):
    db_categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    return db_categoria


@router.patch("/{categoria_id}", response_model=CategoriaOut)
def actualizar_categoria(
    categoria_id: int, cambios: CategoriaUpdate, db: Session = Depends(get_db)
):
    db_categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")

    for campo, valor in cambios.model_dump(exclude_unset=True).items():
        setattr(db_categoria, campo, valor)

    db.commit()
    db.refresh(db_categoria)
    return db_categoria


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    db_categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    db.delete(db_categoria)
    db.commit()