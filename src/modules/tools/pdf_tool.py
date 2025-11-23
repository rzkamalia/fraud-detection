from langchain.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from pydantic import SecretStr

from src.core.config import app_config
from src.database import Database


def get_vector_store() -> MongoDBAtlasVectorSearch:
    """Initialize and return the vector store instance.
    """
    embeddings = OpenAIEmbeddings(
        model="qwen/qwen3-embedding-8b",
        api_key=SecretStr(app_config.openrouter_api_key),
        base_url="https://openrouter.ai/api/v1",
    )
    
    collection = Database().get_mongo_db()["pdf_contents_vector_store"]
    
    vector_store = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
    )
    
    return vector_store


vector_store = get_vector_store()


@tool
def search_pdf_contents(query: str) -> str:
    """Retrieve information from PDF contents using vector similarity search.

    Args:
        query (str): The user's search query.
    
    Returns:
        str: Retrieved context from the most relevant PDF sections, formatted
             with document titles and content.
    """
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    results: list = retriever.invoke(query)
   
    if not results:
        return "No relevant information found in the PDF contents."
    
    return results