import asyncio
import random

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from src.core.langfuse import LangfuseConfig
from src.graph import AgentGraph


async def main():
    langfuse_config = LangfuseConfig()
    langfuse_config.setup()
    
    agent_graph = AgentGraph(langfuse_config)
    
    graph = await agent_graph.graph()

    message = "Hi"
    config: RunnableConfig = {
        "configurable": {
            "user_id": int(random.randint(1, 1000)),
        },
        "recursion_limit": 200,
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

    print(result)


if __name__ == "__main__":
    asyncio.run(main())