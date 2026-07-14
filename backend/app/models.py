from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    cuentas = relationship(
        "Cuenta",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )
    categorias = relationship(
        "Categoria",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )
    transacciones = relationship(
        "Transaccion",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )
    presupuestos = relationship(
        "Presupuesto",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )


class Cuenta(Base):
    __tablename__ = "cuentas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
    saldo = Column(Numeric(12, 2), nullable=False, default=0)

    usuario = relationship("Usuario", back_populates="cuentas")
    transacciones = relationship("Transaccion", back_populates="cuenta")


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(String(20), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    usuario = relationship("Usuario", back_populates="categorias")
    transacciones = relationship("Transaccion", back_populates="categoria")
    presupuestos = relationship("Presupuesto", back_populates="categoria")


class Transaccion(Base):
    __tablename__ = "transacciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    cuenta_id = Column(Integer, ForeignKey("cuentas.id"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    monto = Column(Numeric(12, 2), nullable=False)
    tipo = Column(String(20), nullable=False)
    descripcion = Column(String(255), nullable=True)
    fecha = Column(DateTime, nullable=False, default=datetime.utcnow)
    factura_img = Column(String(255), nullable=True)

    usuario = relationship("Usuario", back_populates="transacciones")
    cuenta = relationship("Cuenta", back_populates="transacciones")
    categoria = relationship("Categoria", back_populates="transacciones")


class Presupuesto(Base):
    __tablename__ = "presupuestos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    monto_limite = Column(Numeric(12, 2), nullable=False)
    periodo = Column(String(20), nullable=False)

    usuario = relationship("Usuario", back_populates="presupuestos")
    categoria = relationship("Categoria", back_populates="presupuestos")
