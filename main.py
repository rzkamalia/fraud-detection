import asyncio
import random
import streamlit as st

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from src.core.langfuse import LangfuseConfig
from src.graph import AgentGraph


async def main():
    langfuse_config = LangfuseConfig()
    langfuse_config.setup()
    
    agent_graph = AgentGraph(langfuse_config)
    
    graph = await agent_graph.graph()

    message = "What share of total card fraud value in H1 2023 was due to cross-border transactions?"

    config: RunnableConfig = {
        "configurable": {
            "user_id": int(random.randint(1, 1000)),
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


if __name__ == "__main__":
    asyncio.run(main())