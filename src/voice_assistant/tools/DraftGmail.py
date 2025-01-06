import asyncio
import base64
import os
from datetime import datetime
from email.mime.text import MIMEText
from typing import Any, Dict, Optional

from agency_swarm.tools import BaseTool
from pydantic import Field, PrivateAttr

from voice_assistant.utils.google_services_utils import GoogleServicesUtils


class DraftGmail(BaseTool):
    """A tool to draft an email. Either reply_to_id or recipient must be provided."""

    subject: Optional[str] = Field(None, description="Subject of the email")
    content: str = Field(..., description="Content of the email")
    recipient: Optional[str] = Field(
        None,
        description="Recipient of the email. If not provided, the email will be sent to the recipient in the reply_to_id",
    )
    reply_to_id: Optional[str] = Field(None, description="ID of the email to reply to")
    _service: Optional[GoogleServicesUtils] = PrivateAttr(None)

    async def run(self) -> Dict[str, Any]:
        self._service = await GoogleServicesUtils.authenticate_service("gmail")
        return await self.draft_email()

    async def draft_email(self) -> Dict[str, Any]:
        try:
            message = await asyncio.to_thread(self._create_message)
            draft = await asyncio.to_thread(
                lambda: self._service.users()
                .drafts()
                .create(userId="me", body={"message": message})
                .execute()
            )
            return {
                "draft_id": draft["id"],
                "message": "Email draft created successfully",
                "drafted_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {"error": str(e), "message": "Failed to create email draft"}

    def _create_message(self) -> Dict[str, Any]:
        message = MIMEText(self.content)
        thread_id = None

        if self.reply_to_id:
            original_message = (
                self._service.users()
                .messages()
                .get(userId="me", id=self.reply_to_id, format="full")
                .execute()
            )
            thread_id = original_message.get("threadId")
            if not thread_id:
                raise ValueError("Original message does not have a threadId.")

            headers = original_message["payload"]["headers"]
            original_subject = next(
                (header["value"] for header in headers if header["name"] == "Subject"),
                "No Subject",
            )
            original_from = next(
                (header["value"] for header in headers if header["name"] == "From"),
                "Unknown",
            )
            message["to"] = original_from
            message["subject"] = f"Re: {original_subject}"
            message["In-Reply-To"] = self.reply_to_id
            message["References"] = self.reply_to_id
        else:
            if self.recipient is None:
                raise ValueError("Recipient is required for new emails")

            if self.subject is None:
                raise ValueError("Subject is required for new emails")

            message["to"] = self.recipient
            message["subject"] = self.subject

        message["from"] = os.getenv("EMAIL_SENDER", "sender@example.com")
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        return {"raw": raw_message, "threadId": thread_id}


if __name__ == "__main__":
    import asyncio

    async def main():
        # Example usage for a new email
        tool = DraftGmail(
            subject="Important Meeting",
            content="Hello,\n\nThis is a draft email for our upcoming meeting.\n\nBest regards,\nYour Name",
            recipient="recipient@example.com",
        )
        result = await tool.run()
        print("New email draft:", result)

        # Example usage for a reply
        reply_tool = DraftGmail(
            content="Thank you for your email. I'll review the draft and get back to you soon.",
            reply_to_id="1929188e90b212c3",  # Replace with an actual email ID
        )
        reply_result = await reply_tool.run()
        print("Reply draft:", reply_result)

    asyncio.run(main())
