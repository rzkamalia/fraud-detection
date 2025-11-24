from pydantic import SecretStr

from langchain.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVectorStore

from src.core.config import app_config
from src.database import Database
from src.modules.utils.supervisor_util import format_pdf_search_results


@tool
async def search_pdf_contents(query: str) -> str:
    """Retrieve information from PDF contents using vector similarity search.

    Args:
        query (str): The user's search query.
    
    Returns:
        str: Retrieved context from the most relevant PDF sections, formatted
             with document titles and content.
    """
    embeddings = OpenAIEmbeddings(
        model="qwen/qwen3-embedding-8b",
        api_key=SecretStr(app_config.openrouter_api_key),
        base_url="https://openrouter.ai/api/v1",
    )

    pgvector_engine = Database().get_pgvector_engine()
    store = await PGVectorStore.create(
            embedding_service=embeddings,
            engine=pgvector_engine,
            table_name=app_config.pdf_vector_table_name,
        )
    
    query_vector = embeddings.embed_query(query)
    
    results = await store.asimilarity_search_by_vector(query_vector, k=3)
   
    if not results:
        return "No relevant information found in the PDF contents."
    
    return format_pdf_search_results(results)