import os

import aiohttp
from dotenv import load_dotenv
from slack_sdk.web.async_client import AsyncWebClient

from prisma import Prisma

load_dotenv()


class Environment:
    def __init__(self):
        self.slack_bot_token = os.environ.get("SLACK_BOT_TOKEN", "unset")
        self.slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET", "unset")
        self.slack_app_id = os.environ.get("SLACK_APP_ID", "unset")
        self.database_url = os.environ.get("DATABASE_URL", "unset")
        self.environment = os.environ.get("ENVIRONMENT", "development")

        self.port = int(os.environ.get("PORT", 3000))

        unset = [key for key, value in self.__dict__.items() if value == "unset"]

        if unset:
            raise ValueError(f"Missing environment variables: {', '.join(unset)}")

        self.db = Prisma()

        self.aiohttp_session: aiohttp.ClientSession = None  # type: ignore - initialised in async_init which happens at program start
        self.slack_client = AsyncWebClient(token=self.slack_bot_token)

    async def async_init(self):
        """Initialises the aiohttp session"""
        self.aiohttp_session = aiohttp.ClientSession()

    async def async_close(self):
        """Closes the aiohttp session"""
        if self.aiohttp_session:
            await self.aiohttp_session.close()


env = Environment()
