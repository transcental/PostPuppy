import asyncio
import json
import logging

from postpuppy.utils.env import env
from postpuppy.utils.langs import LANGUAGES
from postpuppy.utils.logging import send_heartbeat
from postpuppy.utils.shipments import find_diff
from postpuppy.utils.shipments import get_shipments


async def check_for_shipment_updates(delay: int = 30):
    while True:
        users = await env.db.user.find_many()
        await send_heartbeat("Starting shipment check")
        for user in users:
            if not user.subscribedChannels or not user.apiUrl:
                continue

            old_shipments = user.shipments if user.shipments else "[{}]"
            new_shipments = json.dumps(await get_shipments(user.id, user.apiUrl))

            if new_shipments == old_shipments:
                await send_heartbeat(f"{user.id}: No changes in shipments")
                continue

            if new_shipments == "[{}]":
                await send_heartbeat(
                    f"{user.id}: New shipments is empty. Viewer is likely down."
                )
                continue

            await env.db.user.update(
                where={"id": user.id}, data={"shipments": new_shipments}
            )

            if old_shipments == "[{}]":
                await send_heartbeat(f"{user.id}: Old shipments is default. Skipping.")
                continue

            try:
                differences = find_diff(
                    json.loads(old_shipments), json.loads(new_shipments)
                )
            except json.JSONDecodeError as e:
                logging.error(e)
                await send_heartbeat(f"{user.id}: Failed to decode JSON {e}")
                continue

            if not differences:
                await send_heartbeat(f"{user.id}: No differences found")
                continue

            await send_heartbeat(
                f"{user.id}: Found differences.",
                messages=[msg["msg"] for msg in differences],
            )
            for channel in user.subscribedChannels:
                if channel.startswith("U"):
                    is_channel = False
                else:
                    channel_info = await env.slack_client.conversations_info(
                        channel=channel
                    )
                    is_channel = channel_info.get("channel", {}).get("is_channel")
                for msg in differences:
                    message = msg["pub_msg"] if is_channel else msg["msg"]
                    lang = LANGUAGES.get(user.language, LANGUAGES["dog"])
                    try:
                        await env.slack_client.chat_postMessage(
                            channel=channel,
                            icon_emoji=lang.get(
                                "icon_emoji", LANGUAGES["dog"]["icon_emoji"]
                            ),
                            username=lang.get(
                                "display_name", LANGUAGES["dog"]["display_name"]
                            ),
                            text="Your shipments have been updated!",
                            unfurl_links=False,
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
                    except Exception as e:
                        await send_heartbeat(
                            f"{user.id}: Failed to send update message to {channel}",
                            [f"```{e}```"],
                        )
                        logging.error(
                            f"Failed to send update message to {channel} ({user.id}\n{e}"
                        )
                        language = LANGUAGES.get(user.language, LANGUAGES["dog"])[
                            "utils.checker"
                        ]
                        blocks = language.get(
                            "cant_send", LANGUAGES["dog"]["cant_send"]
                        ).get("text", LANGUAGES["dog"]["cant_send"]["text"])
                        blocks[0]["text"]["text"].format(channel)
                        await env.slack_client.chat_postMessage(
                            channel=user.id,
                            icon_emoji=lang.get(
                                "icon_emoji", LANGUAGES["dog"]["icon_emoji"]
                            ),
                            username=lang.get(
                                "display_name", LANGUAGES["dog"]["display_name"]
                            ),
                            text=language.get(
                                "cant_send", LANGUAGES["dog"]["cant_send"]
                            )
                            .get("text", LANGUAGES["dog"]["cant_send"]["text"])
                            .format(channel),
                            blocks=blocks,
                        )

        await send_heartbeat("Finished shipment check")
        await asyncio.sleep(delay)
