import os
from agency_swarm.tools import BaseTool
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

# Constants
SLACK_TOKEN = os.getenv('SLACK_BOT_TOKEN')
NUM_MESSAGES = 5

class CheckUnreadSlackMessages(BaseTool):
    """
    Tool to check unread messages in Slack channels and direct messages.
    """

    async def run(self):
        """
        Asynchronously fetches unread messages from Slack channels and direct messages.
        """
        client = AsyncWebClient(token=SLACK_TOKEN)

        try:
            # Fetch conversations list for channels and direct messages
            response = await client.conversations_list(types="public_channel,private_channel,im")
            channels = response['channels']

            unread_messages_summary = []

            for channel in channels:
                # Check if the bot is a member of the channel or if it's a direct message
                if channel.get('is_member', True):  # Direct messages don't have 'is_member'
                    # Fetch channel info to get the last read timestamp
                    channel_info = await client.conversations_info(channel=channel['id'])
                    last_read = channel_info['channel'].get('last_read', '0')

                    # Fetch the most recent messages in each channel or direct message
                    result = await client.conversations_history(channel=channel['id'], limit=NUM_MESSAGES)
                    messages = result['messages']

                    # Find unread messages based on the last read timestamp
                    unread_messages = [msg for msg in messages if msg['ts'] > last_read]

                    if unread_messages:
                        channel_name = channel.get('name') or f"DM with {channel.get('user', 'unknown')}"
                        summary = f"Unread messages in {channel_name}: {len(unread_messages)}"
                        unread_messages_summary.append(summary)
                        for message in unread_messages:
                            unread_messages_summary.append(message['text'])

            if not unread_messages_summary:
                return "No unread messages in any channels or direct messages."

            return "\n".join(unread_messages_summary)

        except SlackApiError as e:
            return f"Error fetching conversations: {e.response['error']}"

if __name__ == "__main__":
    import asyncio

    tool = CheckUnreadSlackMessages()
    print(asyncio.run(tool.run()))