from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pymongo.asynchronous.mongo_client import AsyncMongoClient
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool
from pymongo.asynchronous.database import AsyncDatabase

from src.core.config import Config, app_config


def get_mongo_client(config: Config) -> AsyncMongoClient:
    client = AsyncMongoClient(
        f"mongodb://{config.mongodb_user}:{config.mongodb_pass}@{config.mongodb_host}:{config.mongodb_port}"
    )
    return client


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


mongo_client = get_mongo_client(app_config)
pg_pool = get_postgres_connection_pool(app_config)


class Database:
    def __init__(self):
        self._mongo_client = mongo_client
        self._pg_pool = pg_pool
    
    @asynccontextmanager
    async def get_mongo_db(self) -> AsyncGenerator[AsyncDatabase]:
        try:
            db = self._mongo_client[app_config.mongodb_database]
            yield db
        except Exception:
            raise

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