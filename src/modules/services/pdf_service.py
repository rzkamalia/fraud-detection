from typing import cast

import pymupdf
import pymupdf4llm

from src.core.config import app_config
from src.database import Database


class PdfParserService:

    def __init__(self, db: Database):
        self._db = db

    def _parse_content(self) -> list[dict[str, str]]:
        """Parse the content of a PDF file and return a list of dictionaries containing the text content of each page.

        Returns:
            list[dict[str, str]]: A list of dictionaries containing the text content of each page.
        """
        try:
            document = pymupdf.open(app_config.pdf_filename)
        except Exception as e:
            print(f"Error opening PDF document: {e}")
            return []

        try:
            md_text = pymupdf4llm.to_markdown(document, page_chunks=True, ignore_images=False, ignore_graphics=False)
            md_text = cast(list, md_text)
        except Exception as e:
            print(f"Markdown conversion failed: {e}")
            return []

        pdf_contents = []
        for page in md_text:
            pdf_contents.append(
                {
                    "content": page.get("text"),
                    "page_index": page.get("metadata", {}).get("page"),
                }
            )

        return pdf_contents
    
    async def _insert(self) -> None:
        """Insert PDF content to database.
        """
        pdf_contents = self._parse_content()
        
        try:
            if pdf_contents:
                async with self._db.get_mongo_db() as db:
                    collection = db["pdf_contents"]
                    await collection.insert_many(pdf_contents)
        except Exception as e:
            raise RuntimeError(f"Failed to insert PDF contents into database: {e}") from e

    async def process(self) -> None:
        """Process the PDF file and insert its content into the database.
        """
        await self._insert()