from uuid import uuid4

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph

from src.core.langfuse import LangfuseConfig
from src.database import Database
from src.graph import AgentGraph
from src.modules.schemas.state_schema import Configuration, State


async def initialize_backend() -> tuple[Database, CompiledStateGraph[State, Configuration]]:
    """Initialize database and graph components.

    Returns:
        Tuple[Database, CompiledStateGraph[State, Configuration]]: The database and compiled graph.
    """
    db = Database()
    await db.pg_pool_open()
    await db.setup_checkpointer()

    langfuse_config = LangfuseConfig()
    langfuse_config.setup()
    
    agent_graph = AgentGraph(db, langfuse_config)
    graph = await agent_graph.graph()
    
    return db, graph


async def process_message(graph, message: str) -> str:
    """Process a user message and return the response.

    Args:
        graph (CompiledStateGraph): The compiled agent graph.
        message (str): The user message.
    
    Returns:
        str: The response from the agent.
    """
    config: RunnableConfig = {
        "configurable": {
            "thread_id": str(uuid4()),
        },
    }
    
    result = await graph.ainvoke(
        input={
            "messages": [
                HumanMessage(content=message),
            ],
        },
        config=config,
    )
    
    return result["messages"][-1].content