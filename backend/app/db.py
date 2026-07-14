from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from app.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./gestor_finanzas.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def ensure_schema() -> None:
    inspector = inspect(engine)
    if "transacciones" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("transacciones")}
        if "cuenta_id" not in columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE transacciones ADD COLUMN cuenta_id INTEGER"))

    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependencia de FastAPI: entrega una sesión y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()