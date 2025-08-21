import logging
from collections.abc import AsyncGenerator, Callable
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command

from .llm import LLM

logger = logging.getLogger(__name__)


class AgentMetaclass(type):
    """Agent metaclass to enable replication of agents."""

    # TODO@Collins: Implement this metaclass
    pass


class BaseAgent(metaclass=AgentMetaclass):
    """Manages the execution and lifecycle of every agent.

    Defines the same graph structure for each agent. An LLM node, which takes on the
    name of the subclass, and a tools node. The tools node, can be functions or
    sub-agents.
    """

    llm: LLM = LLM()
    overall_state = None

    tools: list[Callable] | None = None
    graph: CompiledStateGraph | None = None
    config: dict[str, Any] | None = None
    checkpointer: InMemorySaver | None = None
    system_message: SystemMessage | None = None

    async def llm_node[State](self, state: State) -> State:
        """Graph reasoning (llm) node."""
        messages = self.system_message + state["messages"]

        response = await self.llm.invoke(messages)

        return {"messages": [response]}

    def _build_graph_input(
        self, initial_state: str | list[dict[str, Any]]
    ) -> dict[str, list] | Command:
        """Build the input for intiating graph execution."""
        logger.debug("Building graph input, %s", initial_state)
        if isinstance(initial_state, str):
            return {"messages": [HumanMessage(content=initial_state)]}
        elif isinstance(initial_state, list):
            return Command(resume=initial_state)

        raise Exception("Invalid initial state.")

    def _build_graph(self) -> CompiledStateGraph:
        """Build and compile agent graph."""
        builder = StateGraph(self.overall_state)
        llm_node_name = self.__class__.__name__.lower()
        nodes = [(llm_node_name, self.llm_node)]

        if self.tools:
            nodes.append(("tools", ToolNode(self.tools)))

        for node_name, node in nodes:
            builder.add_node(node_name, node)

        builder.add_edge(START, llm_node_name)
        builder.add_conditional_edges(llm_node_name, tools_condition)
        builder.add_edge("tools", llm_node_name)

        return builder.compile(checkpointer=self.checkpointer)

    async def run(
        self,
        initial_state: str | list[dict[str, Any]],
    ) -> AsyncGenerator[Any, Any, None]:
        """Async entry point to every agent.

        Args:
            initial_state (str | list[dict[str, Any]]): The input to the graph.

        Yields:
            Iterator[AsyncGenerator[Any, Any, None]]: A message, tool call or an
                interrupt.

        """
        if not self.graph:
            self.graph = self._build_graph()

        async for _stream_mode, chunk in self.graph.astream(
            self._build_graph_input(initial_state),
            config=self.config,
            stream_mode=["messages", "custom"],
        ):
            yield chunk[0]

        interrupts = self.graph.get_state(self.config).interrupts

        if len(interrupts) > 0:
            yield interrupts[0]
