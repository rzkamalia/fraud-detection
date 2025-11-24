import pymupdf
import pymupdf4llm
from pydantic import SecretStr
from typing import cast

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVectorStore

from src.core.config import app_config
from src.database import Database


class PdfParserService:

    def __init__(self, db: Database):
        self._db = db

    def _parse_content(self) -> list[Document]:
        """Parse the content of a PDF file and return a list of Document objects containing the text content of each page.

        Returns:
            list[Document]: A list of Document objects containing the text content of each page.
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
        finally:
            if document is not None:
                document.close()

        pdf_contents = []
        for page in md_text:
            pdf_contents.append(
                Document(
                    page_content=page.get("text"),
                    metadata={
                        "page": page.get("metadata", {}).get("page")
                    },
                )
            )

        return pdf_contents
    
    async def _insert(self) -> None:
        """Insert PDF content to database.
        """
        pgvector_engine = self._db.get_pgvector_engine()
        await pgvector_engine.ainit_vectorstore_table(
            table_name=app_config.pdf_vector_table_name,
            vector_size=4096,
        )

        docs = self._parse_content()
        if not docs:
            raise ValueError("No docs (PDF contents) to insert.")

        embeddings = OpenAIEmbeddings(
                model="qwen/qwen3-embedding-8b",
                api_key=SecretStr(app_config.openrouter_api_key),
                base_url="https://openrouter.ai/api/v1",
            )

        store = await PGVectorStore.create(
            embedding_service=embeddings,
            engine=pgvector_engine,
            table_name=app_config.pdf_vector_table_name,
        )

        await store.aadd_documents(docs)

    async def process(self) -> None:
        """Process the PDF file and insert its content into the database.
        """
        await self._insert()