import os

from aiohttp import ClientSession
from dotenv import load_dotenv
from slack_sdk.web.async_client import AsyncWebClient

from prisma import Prisma

load_dotenv()


class Environment:
    def __init__(self):
        self.slack_bot_token = os.environ.get("SLACK_BOT_TOKEN", "unset")
        self.slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET", "unset")
        self.slack_app_id = os.environ.get("SLACK_APP_ID", "unset")
        self.slack_heartbeat_channel = os.environ.get(
            "SLACK_HEARTBEAT_CHANNEL", "unset"
        )

        self.database_url = os.environ.get("DATABASE_URL", "unset")
        self.environment = os.environ.get("ENVIRONMENT", "development")
        self.shipment_viewer_token = os.environ.get("SHIPMENT_VIEWER_TOKEN", "unset")

        self.port = int(os.environ.get("PORT", 3000))

        self.loops_transactional_id = os.environ.get("LOOPS_TRANSACTIONAL_ID", "unset")
        self.loops_api_key = os.environ.get("LOOPS_API_KEY", "unset")

        self.domain = os.environ.get("DOMAIN", "unset")
        self.aiohttp_session: ClientSession

        unset = [key for key, value in self.__dict__.items() if value == "unset"]

        if unset:
            raise ValueError(f"Missing environment variables: {', '.join(unset)}")

        self.db = Prisma()

        self.slack_client = AsyncWebClient(token=self.slack_bot_token)


env = Environment()
