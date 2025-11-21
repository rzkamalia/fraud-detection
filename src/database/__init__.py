from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

from src.core.config import Config, app_config


def get_postgres_connection_pool(config: Config) -> AsyncConnectionPool:
    pool = AsyncConnectionPool(
        conninfo=(
            f"dbname={config.postgres_db} "
            f"user={config.postgres_user} "
            f"password={config.postgres_pass} "
            f"host={config.postgres_host} "
            f"port={config.postgres_port}"
        ),
        open=False,
        timeout=app_config.postgres_timeout,    
    )
    return pool


pg_pool = get_postgres_connection_pool(app_config)


class Database:
    def __init__(self):
        self._pg_pool = pg_pool
    
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
