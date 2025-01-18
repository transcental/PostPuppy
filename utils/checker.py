import asyncio
import json
import logging

from utils.env import env
from utils.shipments import find_diff
from utils.shipments import get_shipments


async def check_for_shipment_updates(delay: int = 10):
    users = await env.db.user.find_many()
    while True:
        for user in users:
            if not user.apiUrl:
                continue
            logging.info(f"Checking for user {user.id}")
            old_shipments = json.dumps(user.shipments) or ""
            new_shipments = json.dumps(await get_shipments(user.id, user.apiUrl))
            await env.db.user.update(
                where={"id": user.id}, data={"shipments": new_shipments}
            )

            with open("old_shipments.json", "w") as f:
                f.write(old_shipments)

            with open("new_shipments.json", "w") as f:
                f.write(new_shipments)
            if not new_shipments or not old_shipments or new_shipments == old_shipments:
                continue

            try:
                old_shipments_dict = json.loads(old_shipments)
                new_shipments_dict = json.loads(new_shipments)
                differences = find_diff(old_shipments_dict, new_shipments_dict)
            except json.JSONDecodeError as e:
                logging.error(e)
                continue

            if not differences:
                continue

            for channel in user.subscribedChannels:
                for msg in differences:
                    await env.slack_client.chat_postMessage(
                        channel=channel,
                        text="Your shipments have been updated!",
                        blocks=[
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": msg,
                                },
                            }
                        ],
                    )

        await asyncio.sleep(delay)
