from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from langchain_postgres import PGEngine
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

from src.core.config import app_config


def get_postgres_connection_pool() -> AsyncConnectionPool:
    pool = AsyncConnectionPool(
        conninfo=(
            f"dbname={app_config.postgres_db} "
            f"user={app_config.postgres_user} "
            f"password={app_config.postgres_pass} "
            f"host={app_config.postgres_host} "
            f"port={app_config.postgres_port}"
        ),
        open=False,
        timeout=app_config.postgres_timeout,    
    )
    return pool

def get_pgvector_engine_connection_pool() -> PGEngine:
    return PGEngine.from_connection_string(
        url=f"postgresql+asyncpg://{app_config.postgres_user}:{app_config.postgres_pass}@{app_config.postgres_host}:{app_config.postgres_port}/{app_config.postgres_db}"
    )


pg_pool = get_postgres_connection_pool()
pgvector_engine_pool = get_pgvector_engine_connection_pool()


class Database:
    def __init__(self):
        self._pg_pool = pg_pool
        self._pgvector_engine_pool = pgvector_engine_pool
        
    @asynccontextmanager
    async def get_postgres_db(self) -> AsyncGenerator[AsyncConnection]:
        if self._pg_pool.closed:
            await self._pg_pool.open()
        
        async with self._pg_pool.connection() as conn:
            try:
                yield conn
            except Exception:
                await conn.rollback()
                raise

    def get_pgvector_engine(self) -> PGEngine:
        return self._pgvector_engine_pool