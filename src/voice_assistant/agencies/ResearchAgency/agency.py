from agency_swarm import Agency

from .AnalystAgent.AnalystAgent import AnalystAgent
from .BrowsingAgent.BrowsingAgent import BrowsingAgent


def create_agency():
    browsing_agent = BrowsingAgent()
    analyst_agent = AnalystAgent()

    agency = Agency(
        [
            analyst_agent,
            [analyst_agent, browsing_agent],
        ],
        shared_instructions="agency_manifesto.md",
        temperature=0.0,
        max_prompt_tokens=25000,
        async_mode="threading",
    )

    return agency


agency = create_agency()


if __name__ == "__main__":
    agency.run_demo()
