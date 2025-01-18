import asyncio
import json
import logging

from utils.env import env
from utils.shipments import find_diff
from utils.shipments import get_shipments


async def check_for_shipment_updates(delay: int = 10):
    while True:
        users = await env.db.user.find_many()
        for user in users:
            if not user.subscribedChannels or not user.apiUrl:
                continue

            logging.info(f"Checking for user {user.id}")
            old_shipments = user.shipments if user.shipments else "[{}]"
            new_shipments = json.dumps(await get_shipments(user.id, user.apiUrl))
            await env.db.user.update(
                where={"id": user.id}, data={"shipments": new_shipments}
            )

            if new_shipments == old_shipments:
                continue

            if old_shipments == "[{}]":
                # First run, skip
                continue

            try:
                differences = find_diff(
                    json.loads(old_shipments), json.loads(new_shipments)
                )
            except json.JSONDecodeError as e:
                logging.error(e)
                continue

            if not differences:
                continue

            for channel in user.subscribedChannels:
                if channel.startswith("U"):
                    is_channel = False
                else:
                    logging.info(f"Channel info: {channel}")
                    channel_info = await env.slack_client.conversations_info(
                        channel=channel
                    )
                    is_channel = channel_info.get("channel", {}).get("is_channel")
                for msg in differences:
                    message = msg["pub_msg"] if is_channel else msg["msg"]
                    await env.slack_client.chat_postMessage(
                        channel=channel,
                        text="Your shipments have been updated!",
                        blocks=[
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": message,
                                },
                            }
                        ],
                    )

        await asyncio.sleep(delay)
