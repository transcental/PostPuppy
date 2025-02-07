import os
from smtplib import SMTP

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

        self.smtp_server = os.environ.get("SMTP_SERVER", "unset")
        self.smtp_port = int(os.environ.get("SMTP_PORT", 587))
        self.smtp_sender = os.environ.get("SMTP_SENDER", "unset")
        self.smtp_passowrd = os.environ.get("SMTP_PASSWORD", "unset")

        self.domain = os.environ.get("DOMAIN", "unset")

        unset = [key for key, value in self.__dict__.items() if value == "unset"]

        if unset:
            raise ValueError(f"Missing environment variables: {', '.join(unset)}")

        self.db = Prisma()

        self.slack_client = AsyncWebClient(token=self.slack_bot_token)
        self.smtp_client = SMTP(self.smtp_server, self.smtp_port)
        self.smtp_logged_in = False

    def smtp_login(self):
        if not self.smtp_logged_in:
            self.smtp_client.starttls()
            self.smtp_client.login(self.smtp_sender, self.smtp_passowrd)
            self.smtp_logged_in = True

    def smtp_logout(self):
        if self.smtp_logged_in:
            self.smtp_client.quit()
            self.smtp_logged_in = False


env = Environment()
