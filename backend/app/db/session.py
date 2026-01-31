from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
import logging
from sqlalchemy import text

from app.core.config import DATABASE_URL

logger = logging.getLogger(__name__)

def _prepare_async_url_and_connect_args(database_url: str):
    """
    Ensure the URL uses the asyncpg dialect and convert sslmode/channel_binding
    query params into asyncpg-compatible connect_args (ssl=True).
    Returns: (clean_url, connect_args_dict)
    """
    if not database_url:
        raise RuntimeError("DATABASE_URL must be set in environment")

    # Ensure scheme includes +asyncpg
    if database_url.startswith("postgresql://") and not database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    parsed = urlparse(database_url)
    qs = parse_qs(parsed.query, keep_blank_values=True)

    use_ssl = False
    sslmode = qs.get("sslmode", [None])[0]
    if sslmode:
        if sslmode.lower() in ("require", "verify-ca", "verify-full", "allow"):
            use_ssl = True
    ssl_q = qs.get("ssl", [None])[0]
    if ssl_q and ssl_q.lower() in ("1", "true", "yes", "on"):
        use_ssl = True

    filtered_qs = {k: v for k, v in qs.items() if k not in ("sslmode", "channel_binding")}

    new_query = urlencode(filtered_qs, doseq=True)
    clean_parsed = parsed._replace(query=new_query)
    clean_url = urlunparse(clean_parsed)

    connect_args = {}
    if use_ssl:
        connect_args["ssl"] = True

    logger.debug("Prepared DB URL (hidden) and connect_args=%s", {"ssl": connect_args.get("ssl", False)})
    return clean_url, connect_args

# Build engine and sessionmaker
clean_url, connect_args = _prepare_async_url_and_connect_args(DATABASE_URL)
engine = create_async_engine(clean_url, future=True, echo=False, connect_args=connect_args)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

# Dependency generator for FastAPI endpoints
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        # Force IST timezone at DB session level
        await session.execute(text("SET TIME ZONE 'Asia/Kolkata'"))
        yield session
