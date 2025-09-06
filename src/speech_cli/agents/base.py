# ruff: noqa: PLR0913
from __future__ import annotations

import asyncio
import logging
import traceback
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Annotated

from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, add_messages
from langgraph.types import Command
from pydantic import BaseModel, Field

from speech_cli.core.llm import LLM
from speech_cli.core.utils import connected_to_internet

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable, Hashable
    from types import TracebackType
    from typing import Any

    from langchain_core.language_models.base import LanguageModelInput
    from langchain_core.messages import BaseMessage
    from langchain_core.runnables import Runnable
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.graph.state import CompiledStateGraph

logger = logging.getLogger(__name__)


class BaseState(BaseModel):
    """The base state for all agents state."""

    messages: Annotated[list[AnyMessage], add_messages] = Field(
        description="The conversation history."
    )

    @property
    def next_agent_state_update(self):
        """A mapping of the next agent state keys and respective updates to make."""
        pass


class BaseInputSchema(BaseState):
    """The agents graph input schema."""

    pass


class AgentsGraphState(BaseState):
    """The agents graph overall state."""

    summary: str = Field("", description="Clearly written summary of user's request.")


class BaseAgent(ABC):
    """Base class for every agent.

    Creates every agent and adds all main agents to the agents graph.
    """

    llm: Runnable[LanguageModelInput, BaseMessage] = LLM()

    overall_state = None
    tools: list[Callable] | None = None

    def __init_subclass__(
        cls: BaseAgent,
        sub_agent: bool = False,
        start_node: bool = False,
        next_node: str | Callable | None = None,
        path_map: dict[Hashable, str] | list[str] | None = None,
        end_node: bool = False,
        private_state: bool = False,
    ):
        """Build agent graph for sub classes.

        Args:
            sub_agent (bool, optional): Indicates if agent is a sub agent.
            start_node (bool, optional): Set agent or node as entry node.
            Defaults to False.
            next_node (bool, optional): Set agent or node as next to execute in the
                agents graph.
            path_map (dict, list, optional): The path map for conditional next node.
            end_node (bool): Set agent or node as last to execute in the agents graph.
            private_state (bool): Whether the agent state is private or not.

        """
        super().__init_subclass__()
        builder = StateGraph(cls.overall_state)

        for node_name, node in cls.nodes():
            builder.add_node(node_name, node)

        for from_node, to_node in cls.static_edges():
            builder.add_edge(from_node, to_node)

        for from_node, condition in cls.conditional_edges():
            builder.add_conditional_edges(from_node, condition)

        graph_name = cls.__name__

        graph = builder.compile(name=graph_name)

        if private_state:
            cls.graph = graph
            if isolation_unit := getattr(cls, f"call_{graph_name.lower()}", None):
                graph = isolation_unit
                logger.debug("Create the isolation unit for %s", graph_name)
            else:
                raise NotImplementedError(
                    f"Agent, {graph_name} is meant to be private, but the isolation"
                    f" unit call_{graph_name.lower()} can't be found."
                )

        if not sub_agent:
            cls._add_to_agents_graph(
                graph_name, start_node, next_node, graph, path_map, end_node
            )
        else:
            return graph

    @classmethod
    def _add_to_agents_graph(
        cls,
        name: str,
        start_node: bool,
        next_node: str | Callable | None,
        graph: CompiledStateGraph | Callable,
        path_map: dict[Hashable, str] | list[str] | None,
        end_node: bool,
    ):
        """Add the built graph to the overall agents graph."""
        logger.debug("Adding agent %s to agents graph.", name)

        AgentsGraph.builder.add_node(name, graph)

        if start_node:
            AgentsGraph.builder.set_entry_point(name)
        elif end_node:
            AgentsGraph.builder.set_finish_point(name)

        if next_node:
            if isinstance(next_node, str):
                AgentsGraph.builder.add_edge(name, next_node)
            elif callable(next_node):
                AgentsGraph.builder.add_conditional_edges(
                    name, next_node, path_map=path_map
                )

    @classmethod
    @abstractmethod
    def nodes(cls) -> list[tuple[str, Callable]]:
        """Class method for retrieving agent nodes."""
        ...

    @classmethod
    @abstractmethod
    def static_edges(cls) -> list[tuple[str | list[str], str]]:
        """Class method for retrieving agent static edges."""
        ...

    @classmethod
    @abstractmethod
    def conditional_edges(cls) -> list[tuple[str, Any]]:
        """Class method for retrieving agent conditional edges."""
        ...

    @classmethod
    async def llm_invoke(cls, messages) -> BaseMessage:
        """Asynchronously invoke the right llm for the agent."""
        if not connected_to_internet():
            raise ConnectionError("User is not connected to the internet.")

        try:
            response = cls.llm.ainvoke(messages)
        except Exception as err:
            logger.debug("An error, %s occurred, now retrying after 60s.", err)
            # Wait for 60 secs before retrying, just in case, we ran into usage limit
            await asyncio.sleep(60)
            response = cls.llm.ainvoke(messages)

        return await response


class AgentsGraph:
    """The agents workflow graph."""

    builder = StateGraph(AgentsGraphState, input_schema=BaseInputSchema)
    config: dict[str, Any] | None = {
        "recursion_limit": 500,
        "configurable": {"thread_id": "agents_graph_1"},
    }
    checkpointer = InMemorySaver()
    graph: CompiledStateGraph | None = None

    def __new__(cls, *_args, **_kwargs):
        """Build the agents graph once and store on the class."""
        if not cls.graph:
            logger.debug("Building agents graph again..")
            cls.graph = cls.builder.compile(checkpointer=cls.checkpointer)

        return super().__new__(cls)

    def __init__(self, user_input: str | list[dict[str, Any]]):
        self.user_input = user_input
        self.error: str | None = None
        self.interrupted = False

    def __enter__(self):
        """Return the agent."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        """Capture error if it exists."""
        if exc_val:
            if isinstance(exc_val, ConnectionError):
                self.error = (
                    "Connection error, make sure you are connected to the internet!"
                )
            elif isinstance(exc_val, Exception):
                self.error = "Unknown error encountered, please try again!"
            logger.error(
                "Exception occurred: %s",
                "".join(traceback.format_exception(exc_type, value=exc_val, tb=exc_tb)),
            )
            return True

    @property
    def _graph_input(self) -> dict[str, list] | Command:
        """Build the input for initiating graph execution from user input."""
        logger.debug("Building graph input, %s", self.user_input)
        if isinstance(self.user_input, str):
            return {"messages": [HumanMessage(content=self.user_input)]}
        elif isinstance(self.user_input, list):
            return Command(resume=self.user_input)
        raise Exception("Invalid initial state.")

    async def run(self) -> AsyncGenerator[Any, Any, None]:
        """Async entry point to every agent.

        Args:
            graph_input (str | list[dict[str, Any]]): The input to the graph.

        Yields:
            Iterator[AsyncGenerator[Any, Any, None]]: A message, tool call or an
                interrupt.

        """
        async for _namespace, _stream_mode, chunk in self.graph.astream(
            self._graph_input,
            config=self.config,
            stream_mode=["messages", "custom"],
            subgraphs=True,
        ):
            logger.debug(
                "The graph stream,\nnamespace: %s \nstream mode: %r\nchunk: %r",
                _namespace,
                _stream_mode,
                chunk,
            )
            yield chunk[0]

        interrupts = self.graph.get_state(self.config).interrupts
        if len(interrupts) > 0:
            self.interrupted = True
            yield interrupts[0]
