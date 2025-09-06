import logging
from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# def handoff_tool_with_state(
#     state: Annotated[MessagesState, InjectedState],
#     tool_call_id: Annotated[str, InjectedToolCallId],
# ) -> Command:
#     logger.debug("Transferring to %s, Last agent state: %r", agent_name, state)

#     tool_message = ToolMessage(
#         content=f"Successfully transferred to {agent_name}",
#         name=name,
#         tool_call_id=state.get("tool_call_id"),  # depends on how you store it
#     )

#     return Command(
#         goto=agent_name,
#         update=state.next_agent_state_update,
#     )


def transfer_to_generator(
    summary: str,
    state: Annotated[BaseModel, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Transfer to generator agent."""
    logger.debug(
        "Transferring to Generator with this summary: %s\nAnd this is the injected"
        " state: %r",
        summary,
        state,
    )
    tool_message = ToolMessage(
        content="Successfully transferred to Generator agent.",
        name="transfer_to_generator",
        tool_call_id=tool_call_id,
    )

    return Command(
        graph=Command.PARENT,
        goto="Generator",
        update={"messages": state.messages + [tool_message], "summary": summary},
    )
