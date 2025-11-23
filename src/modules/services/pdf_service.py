import pymupdf
import pymupdf4llm
from pydantic import SecretStr
from typing import cast

from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings

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
        finally:
            if document is not None:
                document.close()

        pdf_contents = []
        for page in md_text:
            pdf_contents.append(
                {
                    "content": page.get("text"),
                    "page_index": page.get("metadata", {}).get("page"),
                }
            )

        return pdf_contents
    
    def _insert(self) -> None:
        """Insert PDF content to database.
        """
        pdf_contents = self._parse_content()
        if not pdf_contents:
            raise ValueError("No PDF content to insert.")

        texts = [page["content"] for page in pdf_contents]
        metadatas = [{"page": page["page_index"]} for page in pdf_contents]

        embeddings = OpenAIEmbeddings(
                model="qwen/qwen3-embedding-8b",
                api_key=SecretStr(app_config.openrouter_api_key),
                base_url="https://openrouter.ai/api/v1",
            )

        collection = self._db.get_mongo_db()["pdf_contents_vector_store"]

        vector_store = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embeddings,
        )

        try:
            vector_store.add_texts(texts=texts, metadatas=metadatas)
        except Exception as e:
            raise RuntimeError(f"Failed to insert PDF embeddings: {e}") from e

    def process(self) -> None:
        """Process the PDF file and insert its content into the database.
        """
        self._insert()