import os

from dataclasses import dataclass, field, fields
from typing import Annotated, Any, TypedDict

from langchain_core.messages import AnyMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


@dataclass(kw_only=True)
class Configuration:
    user_id: int | None = field(default=None)

    @classmethod
    def from_runnable_config(cls, config: RunnableConfig | None = None) -> "Configuration":
        """Create a Configuration object from a RunnableConfig object.

        Args:
            config (Optional[RunnableConfig], optional): RunnableConfig object. Defaults to None.

        Returns:
            Configuration: Configuration object.
        """
        configurable = config["configurable"] if config and "configurable" in config else {}

        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name)) for f in fields(cls) if f.init
        }

        return cls(**{k: v for k, v in values.items() if v})