from pydantic import SecretStr

from langchain.tools import ToolRuntime, tool
from langchain_openai import ChatOpenAI
from langfuse import Langfuse

from src.core.config import app_config
from src.database import Database


@tool
async def search_fraud_records(query: str, runtime: ToolRuntime):
    """Search fraud records in SQL database based on user query.

    Args:
        query (str): The user's search query.
        runtime (ToolRuntime): The runtime context containing state and config.
    """
    configurable = runtime.config.get("configurable", {})

    langfuse_client: Langfuse = configurable.get("langfuse_client")
    if not langfuse_client:
        raise ValueError("Langfuse client is not provided in the configurable.")

    db = Database()
    schema = ""
    async with db.get_postgres_db() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT table_name, column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                ORDER BY table_name, ordinal_position
            """)
            schema_rows = await cursor.fetchall()
            
            # Format schema for the prompt
            current_table = None
            for row in schema_rows:
                table_name, column_name, data_type = row
                if current_table != table_name:
                    schema += f"\n{table_name}:\n"
                    current_table = table_name
                schema += f"  - {column_name}: {data_type}\n"

    prompt = langfuse_client.get_prompt(
        "search_fraud_records",
        label="latest",
        cache_ttl_seconds=600,
    )
    compiled_prompt = prompt.compile(
        schema=schema,
        query=query
    )

    model = prompt.config.get("model")
    temperature = prompt.config.get("temperature", 0.0)

    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=SecretStr(app_config.openrouter_api_key),
        base_url="https://openrouter.ai/api/v1",
    )

    response = await llm.ainvoke(compiled_prompt)

    sql_query = response.content.strip()

    async with db.get_postgres_db() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(sql_query)
            results = await cursor.fetchall()
   
    results_str = str(results)

    return results_str