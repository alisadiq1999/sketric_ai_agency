import asyncio
import logging
import os

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()

logger = logging.getLogger(__name__)


class GoogleServicesUtils:
    """
    Utility class for Gmail and Google Calendar authentication and service creation.
    """

    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.compose",
        "https://www.googleapis.com/auth/calendar.readonly",
    ]

    SERVICE_API_VERSIONS = {"gmail": "v1", "calendar": "v3"}

    @staticmethod
    async def authenticate_service(service_name):
        """
        Authenticates the user and returns a Gmail or Google Calendar service object.
        """

        def authenticate():
            creds = None
            token_path = "token.json"
            credentials_path = "credentials.json"

            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(
                    token_path, GoogleServicesUtils.SCOPES
                )
                logger.info(f"Loaded {service_name} credentials from token.json.")

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info(f"Refreshing expired {service_name} credentials.")
                    creds.refresh(Request())
                else:
                    logger.info(f"Initiating new {service_name} authentication flow.")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, GoogleServicesUtils.SCOPES
                    )
                    creds = flow.run_local_server(port=8080)  # Fixed port
                with open(token_path, "w") as token:
                    token.write(creds.to_json())
                    logger.info(f"Saved new {service_name} credentials to token.json.")

            api_version = GoogleServicesUtils.SERVICE_API_VERSIONS.get(service_name)
            if api_version is None:
                raise ValueError(f"Unsupported service: {service_name}")

            return build(service_name, api_version, credentials=creds)

        try:
            service = await asyncio.to_thread(authenticate)
            logger.info(
                f"{service_name.capitalize()} service authenticated successfully."
            )
            return service
        except Exception as e:
            logger.error(f"Failed to authenticate {service_name} service: {e}")
            raise e

    @staticmethod
    async def authenticate_gmail():
        """
        Authenticates the user and returns a Gmail service object.
        """
        return await GoogleServicesUtils.authenticate_service("gmail")

    @staticmethod
    async def authenticate_calendar():
        """
        Authenticates the user and returns a Google Calendar service object.
        """
        return await GoogleServicesUtils.authenticate_service("calendar")
