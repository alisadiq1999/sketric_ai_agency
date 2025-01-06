from agency_swarm import Agent
from agency_swarm.tools import CodeInterpreter, FileSearch


class AnalystAgent(Agent):
    def __init__(self):
        super().__init__(
            name="AnalystAgent",
            description="Analyzes data, generates insights, and performs complex calculations using code interpreter and file search capabilities.",
            instructions="./instructions.md",
            tools=[CodeInterpreter, FileSearch],
            temperature=0.0,
            max_prompt_tokens=25000,
        )
