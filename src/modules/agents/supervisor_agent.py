from pydantic import SecretStr

from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.config import merge_configs
from langchain_openai import ChatOpenAI

from src.core.config import app_config 
from src.core.langfuse import LangfuseConfig
from src.modules.const.enum import AgentEnum
from src.modules.schemas.state_schema import State
from src.modules.tools.pdf_tool import search_pdf_contents
from src.modules.tools.tabular_data_tool import search_fraud_records
from src.modules.utils.supervisor_util import format_conversation_history


class SupervisorAgent:

    def __init__(self, langfuse_config: LangfuseConfig):
        self._langfuse_config = langfuse_config

    async def _ainvoke_agent(
        self,
        conversation_history: str,
        config: RunnableConfig,
    ) -> dict:
        """Asynchronous invoke the agent.

        Args:
            conversation_history (str): The conversation history.
            config (RunnableConfig): The configuration of the agent.

        Returns:
            dict: The response from the agent.
        """
        prompt = self._langfuse_config._client.get_prompt(
            AgentEnum.SUPERVISOR.value,
            label="latest",
            cache_ttl_seconds=600,
        )
        compiled_prompt = prompt.compile(
            conversation_history=conversation_history,
        )

        model = prompt.config.get("model")
        temperature = prompt.config.get("temperature", 0.0)

        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=SecretStr(app_config.openrouter_api_key),
            base_url="https://openrouter.ai/api/v1",
        )

        tools = [search_fraud_records, search_pdf_contents]
        agent = create_agent(
            model=llm,
            tools=tools,
            middleware=[
                ToolRetryMiddleware(
                    max_retries=1,
                    initial_delay=1.0,
                )
            ]
        )

        merged_configs = merge_configs(
            config,
            {
                "callbacks": [self._langfuse_config._callback],
                "langfuse_client": self._langfuse_config._client,
            },
        )

        return await agent.ainvoke({"messages": compiled_prompt}, merged_configs)

    async def arun(self, state: State, config: RunnableConfig) -> State:
        """Asynchronous run the supervisor agent.

        Args:
            config (RunnableConfig): The configuration of the agent.
            state (State): The state of the agent.

        Returns:
            State: The updated state of the agent.
        """
        conversation_history = format_conversation_history(state["messages"])

        response = await self._ainvoke_agent(
            conversation_history=conversation_history,
            config=config,
        )

        return {
            "messages": [AIMessage(content=response["messages"][-1].content)],
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
