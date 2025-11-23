from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import RetryPolicy

from src.core.langfuse import LangfuseConfig
from src.modules.agents.supervisor_agent import SupervisorAgent
from src.modules.const.enum import AgentEnum
from src.modules.schemas.state_schema import Configuration, State


class AgentGraph:

    def __init__(self, langfuse_config: LangfuseConfig):
        self._supervisor = SupervisorAgent(langfuse_config)

    def builder(self) -> StateGraph[State, Configuration]:
        """Build the agent graph.

        Returns:
            StateGraph: The constructed agent graph.
        """
        builder = StateGraph(state_schema=State, config_schema=Configuration)

        builder.add_node(
            AgentEnum.SUPERVISOR.value,
            self._supervisor.node,
            retry_policy=RetryPolicy(max_attempts=3),
        )

        builder.add_edge(START, AgentEnum.SUPERVISOR.value)
        builder.add_edge(AgentEnum.SUPERVISOR.value, END)

        return builder


    async def graph(self) -> CompiledStateGraph[State, Configuration]:
        """Run the agent graph.

        Returns:
            CompiledStateGraph[State, Configuration]: The compiled agent graph.
        """
        builder = self.builder()
        
        return builder.compile()
