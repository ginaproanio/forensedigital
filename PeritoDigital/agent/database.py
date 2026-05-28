"""Persistencia de conversaciones y deduplicación en PostgreSQL (Supabase)."""
import os
import urllib.parse as urlparse
import re
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, select, Integer, JSON
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la Base de Datos desde .env
DATABASE_URL = os.getenv("DATABASE_URL")
# Asegurar que SQLAlchemy use el driver asyncpg
engine_url = None
connect_args = {}

if DATABASE_URL:
    # Extraer y limpiar la URL para asyncpg usando parsing robusto
    parsed_url = urlparse.urlparse(DATABASE_URL)
    query_params = urlparse.parse_qs(parsed_url.query)
    
    if "options" in query_params:
        options_val = query_params["options"][0]
        # Buscar el search_path dentro del parámetro options (ej: "-c search_path=schema")
        match = re.search(r'search_path=([^ &]+)', options_val)
        if match:
            connect_args["server_settings"] = {"search_path": match.group(1)}
        # Eliminar 'options' para evitar el TypeError en el driver asyncpg
        del query_params["options"]
    
    # Mapeo forense: asyncpg no acepta ssl=true, requiere un modo específico
    if "ssl" in query_params and query_params["ssl"][0].lower() == "true":
        query_params["ssl"] = ["require"]
    
    # Reconstruir la URL sin el parámetro 'options'
    new_query = urlparse.urlencode(query_params, doseq=True)
    engine_url = parsed_url._replace(query=new_query).geturl()

    # Normalización forense del protocolo: soporta postgres:// y postgresql://
    if engine_url:
        engine_url = re.sub(r'^postgres(ql)?://', 'postgresql+asyncpg://', engine_url)
    
    engine = create_async_engine(engine_url, echo=False, connect_args=connect_args)
else:
    raise ValueError("DATABASE_URL no está configurada en las variables de entorno.")

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

class GoogleToken(Base):
    """Modelo para almacenar el token de Google Calendar de forma persistente."""
    __tablename__ = "google_tokens"
    __table_args__ = {"schema": "sorsabsa_identity"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

async def save_google_token(token_data: dict):
    """Guarda o actualiza el token de Google en la base de datos."""
    async with async_session() as session:
        stmt = select(GoogleToken).where(GoogleToken.id == 1)
        result = await session.execute(stmt)
        existing_token = result.scalar_one_or_none()
        if existing_token:
            existing_token.token_data = token_data
        else:
            session.add(GoogleToken(id=1, token_data=token_data))
        await session.commit()

async def get_google_token() -> dict | None:
    """Recupera el token de Google de la base de datos."""
    async with async_session() as session:
        stmt = select(GoogleToken).where(GoogleToken.id == 1)
        result = await session.execute(stmt)
        token_entry = result.scalar_one_or_none()
        return token_entry.token_data if token_entry else None

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
