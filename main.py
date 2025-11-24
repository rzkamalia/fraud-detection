import asyncio
import streamlit as st
from uuid import uuid4

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from src.core.langfuse import LangfuseConfig
from src.database import Database
from src.graph import AgentGraph


async def main():
    db = Database()
    
    await db.pg_pool_open()
    await db.setup_checkpointer()

    langfuse_config = LangfuseConfig()
    langfuse_config.setup()
    
    agent_graph = AgentGraph(db, langfuse_config)
    
    graph = await agent_graph.graph()

    # message = "What share of total card fraud value in H1 2023 was due to cross-border transactions?"
    message = "Europe"

    config: RunnableConfig = {
        "configurable": {
            "thread_id": str(uuid4()),
        },
    }
    
    result = await graph.ainvoke(
        input={
            "messages": [
                HumanMessage(
                    content=message,
                ),
            ],
        },
        config=config,
    )

    print(result["messages"][-1].content)
    
    await db._pg_pool.close()

if __name__ == "__main__":
    asyncio.run(main())