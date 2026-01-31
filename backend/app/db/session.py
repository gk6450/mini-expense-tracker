from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import event
import logging

from app.core.config import DATABASE_URL

logger = logging.getLogger(__name__)

def _prepare_async_url_and_connect_args(database_url: str):
    """
    Ensure asyncpg dialect and convert sslmode/channel_binding
    into asyncpg-compatible connect_args.
    """
    if not database_url:
        raise RuntimeError("DATABASE_URL must be set in environment")

    # Ensure asyncpg driver
    if database_url.startswith("postgresql://") and not database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    parsed = urlparse(database_url)
    qs = parse_qs(parsed.query, keep_blank_values=True)

    use_ssl = False
    sslmode = qs.get("sslmode", [None])[0]
    if sslmode and sslmode.lower() in ("require", "verify-ca", "verify-full", "allow"):
        use_ssl = True

    ssl_q = qs.get("ssl", [None])[0]
    if ssl_q and ssl_q.lower() in ("1", "true", "yes", "on"):
        use_ssl = True

    # Remove unsupported params for asyncpg
    filtered_qs = {k: v for k, v in qs.items() if k not in ("sslmode", "channel_binding")}

    new_query = urlencode(filtered_qs, doseq=True)
    clean_parsed = parsed._replace(query=new_query)
    clean_url = urlunparse(clean_parsed)

    connect_args = {}
    if use_ssl:
        connect_args["ssl"] = True

    logger.info("Database SSL enabled: %s", use_ssl)
    return clean_url, connect_args


# Build engine
clean_url, connect_args = _prepare_async_url_and_connect_args(DATABASE_URL)

engine = create_async_engine(
    clean_url,
    echo=False,
    future=True,
    connect_args=connect_args,
    pool_pre_ping=True,
)

# Enforce IST timezone ON CONNECTION (safe, once per connection)
@event.listens_for(engine.sync_engine, "connect")
def set_postgres_timezone(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
    cursor.close()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()

# FastAPI dependency
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
