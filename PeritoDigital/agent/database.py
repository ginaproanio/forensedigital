"""Persistencia de conversaciones y deduplicación en PostgreSQL (Supabase)."""
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, select, Integer
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la Base de Datos desde .env
DATABASE_URL = os.getenv("DATABASE_URL")
# Asegurar que SQLAlchemy use el driver asyncpg
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Mensaje(Base):
    """Historial de chat persistente."""
    __tablename__ = "agent_messages"
    __table_args__ = {"schema": "sorsabsa_identity"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telefono: Mapped[str] = mapped_column(String(50), index=True)
    rol: Mapped[str] = mapped_column(String(20))  # "user" o "assistant"
    contenido: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ProcessedMessage(Base):
    """Tabla crítica para evitar bloqueos por reintentos de WhatsApp."""
    __tablename__ = "processed_messages"
    __table_args__ = {"schema": "sorsabsa_identity"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

async def init_db():
    """Crea las tablas en el esquema identity si no existen."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def guardar_mensaje(telefono: str, rol: str, contenido: str):
    async with async_session() as session:
        msg = Mensaje(telefono=telefono, rol=rol, contenido=contenido)
        session.add(msg)
        await session.commit()

async def obtener_historial(telefono: str, limite: int = 10) -> list[dict]:
    async with async_session() as session:
        query = select(Mensaje).where(Mensaje.telefono == telefono).order_by(Mensaje.timestamp.desc()).limit(limite)
        result = await session.execute(query)
        rows = result.scalars().all()
        return [{"role": r.rol, "content": r.contenido} for r in reversed(rows)]

async def is_message_processed(message_id: str) -> bool:
    """Verifica si el mensaje ya existe en la DB para evitar duplicados."""
    if not message_id: return False
    async with async_session() as session:
        query = select(ProcessedMessage).where(ProcessedMessage.message_id == message_id)
        result = await session.execute(query)
        return result.scalar_one_or_none() is not None

async def save_processed_message(message_id: str):
    """Registra el ID del mensaje como procesado."""
    if not message_id: return
    async with async_session() as session:
        pm = ProcessedMessage(message_id=message_id)
        session.add(pm)
        await session.commit()
