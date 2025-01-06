"""
This tool allows you to send a message to a specific agent within a specified agency without waiting for a response.

To use this tool, provide the message you want to send, the name of the agency to which the agent belongs, and optionally the name of the agent to whom the message should be sent. If the agent name is not specified, the message will be sent to the default agent for that agency.
"""

import asyncio
import logging

from agency_swarm.agency import Agency
from agency_swarm.threads import Thread
from agency_swarm.threads.thread_async import ThreadAsync
from agency_swarm.tools import BaseTool
from pydantic import Field

from voice_assistant.agencies import AGENCIES, AGENCIES_AND_AGENTS_STRING
from voice_assistant.utils.decorators import timeit_decorator

logger = logging.getLogger(__name__)


class SendMessageAsync(BaseTool):
    """
    Sends a message to a specific agent within a specified agency without waiting for an immediate response.

    Use this tool to initiate long-running tasks asynchronously.
    After sending the message, you can use the 'GetResponse' tool with the same 'agency_name' and 'agent_name' values to check the status or retrieve the agent's response.
    This allows you to perform other tasks or interact with the user while the agent processes the request.

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

    @timeit_decorator
    async def run(self) -> str:
        result = await self.send_message()
        return str(result)

    async def send_message(self) -> str:
        agency: Agency | None = AGENCIES.get(self.agency_name)
        if not agency:
            return f"Agency '{self.agency_name}' not found"

        if not self.agent_name or self.agent_name == agency.ceo.name:
            thread: Thread = agency.main_thread
        else:
            recipient_agent = next(
                (agent for agent in agency.agents if agent.name == self.agent_name),
                None,
            )
            if not recipient_agent:
                return f"Agent '{self.agent_name}' not found in agency '{self.agency_name}'. Available agents: {', '.join(agent.name for agent in agency.agents)}"

            thread: Thread = agency.agents_and_threads.get(agency.ceo.name, {}).get(
                self.agent_name
            )

        if isinstance(thread, ThreadAsync):
            return await asyncio.to_thread(
                thread.get_completion_async,
                message=self.message,
                recipient_agent=recipient_agent,
            )
        else:
            await asyncio.to_thread(
                thread.get_completion,
                message=self.message,
                recipient_agent=recipient_agent,
            )
        return f"Message sent asynchronously. Use 'GetResponse' to check status."


# Dynamically update the class docstring with the list of agencies and their agents
SendMessageAsync.__doc__ = SendMessageAsync.__doc__.format(
    agency_agents=AGENCIES_AND_AGENTS_STRING
)


if __name__ == "__main__":
    tool = SendMessageAsync(
        message="Write a long paragraph about the history of the internet.",
        agency_name="ResearchAgency",
        agent_name="BrowsingAgent",
    )
    print(asyncio.run(tool.run()))

    tool = SendMessageAsync(
        message="Write a long paragraph about the history of the internet.",
        agency_name="ResearchAgency",
        agent_name=None,
    )
    print(asyncio.run(tool.run()))
