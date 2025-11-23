from pydantic import SecretStr

from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from src.core.config import app_config
from src.modules.const.enum import AgentEnum
from src.modules.schemas.state_schema import State
from src.modules.utils.supervisor_util import format_conversation_history

class SupervisorAgent:

    def __init__(self):
        pass

    async def _ainvoke_agent(
        self,
        conversation_history: str,
        config: RunnableConfig,
    ) -> str:
        """Asynchronous invoke the agent.

        Args:
            conversation_history (str): The conversation history.
            config (RunnableConfig): The configuration of the agent.

        Returns:
            str: The result of the agent invocation.
        """
        prompt = self._langfuse.client.get_prompt(
            AgentEnum.SUPERVISOR.value,
            label="latest",
            cache_ttl_seconds=600,
        )
        compiled_prompt = prompt.compile(
            conversation_history=conversation_history,
        )

        model = config.get("model")
        temperature = config.get("temperature", 1.0)

        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=SecretStr(app_config.openai_api_key),
        )

        tools = [pdf_extractor, text2sql]
        agent = create_agent(
            model=llm,
            tools=tools,
        )

        return await agent.ainvoke({"messages": compiled_prompt}, config)

    async def arun(self, state: State, config: RunnableConfig) -> State:
        """Asynchronous run the supervisor agent.

        Args:
            config (RunnableConfig): The configuration of the agent.
            state (State): The state of the agent.

        Returns:
            State: The updated state of the agent.
        """
        conversation_history = format_conversation_history(state["messages"])

        result = await self._ainvoke_agent(
            conversation_history=conversation_history,
            config=config,
        )

        return {
            "messages": [AIMessage(content=result)],
        }

    async def node(self, state: State, config: RunnableConfig) -> State:
        """Run the supervisor agent.

        Args:
            config (RunnableConfig): The configuration of the agent.
            state (State): The state of the agent.

        Returns:
            State: The updated state of the agent.
        """
        return await self.arun(state, config)
