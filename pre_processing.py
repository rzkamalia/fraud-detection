import asyncio

from src.database import Database
from src.modules.services.tabular_data_service import TabularDataService


db = Database()
tabular_data_service = TabularDataService(db)

async def pre_process():
    try:
        await tabular_data_service.process()
    except Exception as e:
        raise RuntimeError(f"An error occurred during pre-processing: {e}") from e
    finally:
        await db._pg_pool.close()

if __name__ == "__main__":
    asyncio.run(pre_process())