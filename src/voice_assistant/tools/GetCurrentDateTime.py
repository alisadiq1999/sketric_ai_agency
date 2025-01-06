import asyncio
from datetime import datetime

from agency_swarm.tools import BaseTool


class GetCurrentDateTime(BaseTool):
    """A tool to get the current date, time, and day of the week."""

    async def run(self) -> str:
        return datetime.now().strftime("%A, %Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    tool = GetCurrentDateTime()
    print(asyncio.run(tool.run()))
