import asyncio

from src.database import Database
from src.modules.services.pdf_service import PdfParserService
from src.modules.services.tabular_data_service import TabularDataService


db = Database()
pdf_parser_service = PdfParserService(db)
tabular_data_service = TabularDataService(db)

async def pre_process():
    try:
        pdf_parser_service.process()
        await tabular_data_service.process()
    except Exception as e:
        raise RuntimeError(f"An error occurred during pre-processing: {e}") from e
    finally:
        db._mongo_client.close()
        await db._pg_pool.close()

if __name__ == "__main__":
    asyncio.run(pre_process())  # run once