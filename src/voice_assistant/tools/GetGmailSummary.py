import asyncio
import base64
import logging
import re
from datetime import datetime, timedelta
from typing import List, Optional

from agency_swarm.tools import BaseTool
from dotenv import load_dotenv
from pydantic import Field, PrivateAttr

from voice_assistant.models import ModelName
from voice_assistant.utils.google_services_utils import GoogleServicesUtils
from voice_assistant.utils.llm_utils import get_model_completion

logger = logging.getLogger(__name__)

load_dotenv()


class GetGmailSummary(BaseTool):
    """A tool to summarize unread Gmail messages from the last two days."""

    max_results: int = Field(
        default=10,
        description="Maximum number of unread emails to fetch. Defaults to 10.",
    )
    _service: Optional[GoogleServicesUtils] = PrivateAttr(None)

    async def run(self) -> str:
        """
        Main execution method to fetch and summarize unread Gmail messages.
        """
        logger.info("Starting Gmail authentication.")
        self._service = await GoogleServicesUtils.authenticate_service("gmail")

        logger.info("Fetching unread messages.")
        messages = await self._fetch_unread_messages()

        if not messages:
            logger.info("No unread messages found.")
            return "No unread Gmail messages found in the last two days."

        logger.info("Summarizing messages using GPT-4o-mini.")
        summary = await self._summarize_messages_with_gpt(messages)

        logger.info("Gmail summary completed.")
        return summary

    async def _fetch_unread_messages(self) -> List[dict]:
        """
        Fetch unread messages from the last two days.
        """
        two_days_ago = (datetime.now() - timedelta(days=2)).strftime("%Y/%m/%d")
        query = f"is:unread after:{two_days_ago}"
        logger.info(f"Executing query: {query}")

        results = await asyncio.to_thread(
            lambda: self._service.users()
            .messages()
            .list(userId="me", q=query, maxResults=self.max_results)
            .execute()
        )

        messages = results.get("messages", [])
        full_messages = []
        logger.info(f"Number of messages fetched: {len(messages)}")

        for message in messages:
            msg = await asyncio.to_thread(
                lambda: self._service.users()
                .messages()
                .get(userId="me", id=message["id"], format="full")
                .execute()
            )
            msg["id"] = message["id"]
            full_messages.append(msg)

        logger.info("All messages fetched successfully.")
        return full_messages

    async def _summarize_messages_with_gpt(self, messages: List[dict]) -> str:
        """
        Summarize the given messages using GPT model.
        """
        full_texts = []
        for msg in messages:
            email_data = self._extract_email_data(msg)
            full_texts.append(self._format_email_text(email_data))

        prompt = (
            "Please provide a summary of the following emails. "
            "For each email, include the email ID, subject, sender, date, "
            "and a brief summary of the content without too many details.\n\n"
        )
        summary = await get_model_completion(
            prompt + "\n\n".join(full_texts),
            ModelName.FAST_MODEL,
        )
        return summary

    def _extract_email_data(self, msg: dict) -> dict:
        """
        Extract relevant data from an email message.
        """
        payload = msg["payload"]
        headers = payload.get("headers", [])
        return {
            "id": msg.get("id", "Unknown ID"),
            "subject": next(
                (h["value"] for h in headers if h["name"] == "Subject"), "No Subject"
            ),
            "from": next(
                (h["value"] for h in headers if h["name"] == "From"), "Unknown Sender"
            ),
            "date": next(
                (h["value"] for h in headers if h["name"] == "Date"), "Unknown Date"
            ),
            "body": self._extract_body(payload),
        }

    def _format_email_text(self, email_data: dict) -> str:
        """
        Format email data into a string representation.
        """
        return (
            f"Email ID: {email_data['id']}\n"
            f"From: {email_data['from']}\n"
            f"Date: {email_data['date']}\n"
            f"Subject: {email_data['subject']}\n"
            f"Body: {email_data['body']}\n"
        )

    def _extract_body(self, payload: dict) -> str:
        """
        Extract the body from an email payload, handling various MIME types and nested parts.
        """
        if "parts" in payload:
            body = self._recursive_extract(payload["parts"])
            if body:
                return body

        # Fallback to the main body if no parts are found
        data = payload.get("body", {}).get("data", "")
        if data:
            try:
                decoded_body = base64.urlsafe_b64decode(data).decode("utf-8")
                return self._remove_links(decoded_body)
            except Exception as e:
                logger.error(f"Error decoding main body: {e}")
        return "No body content"

    def _recursive_extract(self, parts: List[dict]) -> str:
        """
        Recursively extract the body from email parts.
        """
        for part in parts:
            mime_type = part.get("mimeType", "")
            body = part.get("body", {})
            data = body.get("data", "")

            if data and mime_type in ["text/plain", "text/html"]:
                try:
                    decoded_body = base64.urlsafe_b64decode(data).decode("utf-8")
                    return self._remove_links(decoded_body)
                except Exception as e:
                    logger.error(f"Error decoding {mime_type} part: {e}")
            elif "parts" in part:
                result = self._recursive_extract(part["parts"])
                if result:
                    return result
        return ""

    def _remove_links(self, text: str) -> str:
        """
        Remove URLs from the given text.
        """
        url_pattern = re.compile(r"http\S+|www\.\S+")
        cleaned_text = url_pattern.sub("", text)
        logger.debug("Removed links from the email body.")
        return cleaned_text


if __name__ == "__main__":

    async def main():
        tool = GetGmailSummary(max_results=5)
        result = await tool.run()
        print(result)

    asyncio.run(main())
