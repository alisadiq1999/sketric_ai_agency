"""
This tool allows you to send a message to a specific agent within a specified agency and receive a response.

To use this tool, provide the message you want to send, the name of the agency to which the agent belongs, and optionally the name of the agent to whom the message should be sent. If the agent name is not specified, the message will be sent to the default agent for that agency.
"""

import asyncio

from agency_swarm.tools import BaseTool
from pydantic import Field

from voice_assistant.agencies import AGENCIES, AGENCIES_AND_AGENTS_STRING
from voice_assistant.utils.decorators import timeit_decorator


class SendMessage(BaseTool):
    """
    Sends a message to a specific agent within a specified agency and waits for an immediate response.

    Use this tool for direct, synchronous communication with agents for tasks that can be completed quickly.
    The agent processes the message and returns a response immediately.
    If 'agent_name' is not provided, the message is sent to the main agent in the agency.

    To continue the dialogue, invoke this tool again with your follow-up message.
    Note: You are responsible for relaying the agent's responses back to the user.
    Do not send more than one message at a time.

    Available Agencies and Agents:
    {agency_agents}
    """

    message: str = Field(..., description="The message to be sent.")
    agency_name: str = Field(
        ..., description="The name of the agency to send the message to."
    )
    agent_name: str | None = Field(
        None,
        description="The name of the agent to send the message to, or None to use the default agent.",
    )

    def __init__(self, **data):
        super().__init__(**data)

    @timeit_decorator
    async def run(self) -> str:
        result = await self._send_message()
        return str(result)

    async def _send_message(self) -> str:
        agency = AGENCIES.get(self.agency_name)
        if agency:
            recipient_agent = None
            if self.agent_name:
                recipient_agent = next(
                    (agent for agent in agency.agents if agent.name == self.agent_name),
                    None,
                )
                if not recipient_agent:
                    return f"Agent '{self.agent_name}' not found in agency '{self.agency_name}'. Available agents: {', '.join(agent.name for agent in agency.agents)}"
            else:
                recipient_agent = None

            response = await asyncio.to_thread(
                agency.get_completion,
                message=self.message,
                recipient_agent=recipient_agent,
            )
            return response
        else:
            return f"Agency '{self.agency_name}' not found"


# Dynamically update the class docstring with the list of agencies and their agents
SendMessage.__doc__ = SendMessage.__doc__.format(
    agency_agents=AGENCIES_AND_AGENTS_STRING
)


if __name__ == "__main__":
    tool = SendMessage(
        message="Hello, how are you?",
        agency_name="ResearchAgency",
        agent_name="BrowsingAgent",
    )
    print(asyncio.run(tool.run()))

    tool = SendMessage(
        message="Hello, how are you?",
        agency_name="ResearchAgency",
        agent_name=None,
    )
    print(asyncio.run(tool.run()))
