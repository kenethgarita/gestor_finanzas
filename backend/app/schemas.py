from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr

# ---------------------------------------------------------------------------
# Usuario
# ---------------------------------------------------------------------------


class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr


class UsuarioCreate(UsuarioBase):
    password: str  # texto plano recibido en el request, se hashea antes de guardar


class UsuarioUpdate(BaseModel):
    # Todos opcionales: el cliente solo manda los campos que quiere cambiar
    nombre: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class UsuarioOut(UsuarioBase):
    id: int

    # Permite que Pydantic lea directamente el objeto ORM de SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Cuenta
# ---------------------------------------------------------------------------


class CuentaBase(BaseModel):
    nombre: str
    saldo: Decimal = Decimal("0")


class CuentaCreate(CuentaBase):
    usuario_id: int


class CuentaUpdate(BaseModel):
    nombre: str | None = None
    saldo: Decimal | None = None


class CuentaOut(CuentaBase):
    id: int
    usuario_id: int

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Categoria
# ---------------------------------------------------------------------------

TipoCategoria = Literal["ingreso", "gasto"]


class CategoriaBase(BaseModel):
    nombre: str
    tipo: TipoCategoria


class CategoriaCreate(CategoriaBase):
    usuario_id: int


class CategoriaUpdate(BaseModel):
    nombre: str | None = None
    tipo: TipoCategoria | None = None


class CategoriaOut(CategoriaBase):
    id: int
    usuario_id: int

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Transaccion
# ---------------------------------------------------------------------------

TipoTransaccion = Literal["ingreso", "gasto"]


class TransaccionBase(BaseModel):
    monto: Decimal
    tipo: TipoTransaccion
    descripcion: str | None = None
    factura_img: str | None = None


class TransaccionCreate(TransaccionBase):
    usuario_id: int
    categoria_id: int
    fecha: datetime | None = None  # si no se manda, se usa datetime.utcnow()


class TransaccionUpdate(BaseModel):
    categoria_id: int | None = None
    monto: Decimal | None = None
    tipo: TipoTransaccion | None = None
    descripcion: str | None = None
    factura_img: str | None = None
    fecha: datetime | None = None


class TransaccionOut(TransaccionBase):
    id: int
    usuario_id: int
    categoria_id: int
    fecha: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Presupuesto
# ---------------------------------------------------------------------------

PeriodoPresupuesto = Literal["semanal", "mensual", "anual"]


class PresupuestoBase(BaseModel):
    monto_limite: Decimal
    periodo: PeriodoPresupuesto


class PresupuestoCreate(PresupuestoBase):
    usuario_id: int
    categoria_id: int


class PresupuestoUpdate(BaseModel):
    categoria_id: int | None = None
    monto_limite: Decimal | None = None
    periodo: PeriodoPresupuesto | None = None


class PresupuestoOut(PresupuestoBase):
    id: int
    usuario_id: int
    categoria_id: int

    model_config = ConfigDict(from_attributes=True)