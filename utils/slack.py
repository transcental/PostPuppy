import logging
import re

from slack_bolt.async_app import AsyncAck
from slack_bolt.async_app import AsyncApp
from slack_sdk.web.async_client import AsyncWebClient

from utils.env import env
from views.home import generate_home
from views.settings import generate_settings

app = AsyncApp(token=env.slack_bot_token, signing_secret=env.slack_signing_secret)


@app.event("app_home_opened")
async def update_home_tab(client: AsyncWebClient, event, logger):
    user_id = event["user"]
    view = await generate_home(user_id)
    await client.views_publish(user_id=user_id, view=view)


@app.action("open_settings")
async def open_settings(ack: AsyncAck, body, client: AsyncWebClient):
    await ack()
    user_id = body["user"]["id"]
    view = await generate_settings(user_id)
    await client.views_open(trigger_id=body["trigger_id"], view=view)


@app.action("channels_select")
async def channels_callback(ack: AsyncAck, body, client: AsyncWebClient):
    await ack()
    user_id = body["user"]["id"]
    view = body["view"]
    actions = view["state"]["values"]
    selected_channels = actions["channels"]["channels_select"]["selected_conversations"]

    user = await env.db.user.find_first(where={"id": user_id})
    if not user:
        return
    current_channels = user.subscribedChannels or []
    new_channels = [
        channel for channel in selected_channels if channel not in current_channels
    ]
    removed_channels = [
        channel for channel in current_channels if channel not in selected_channels
    ]

    for channel in new_channels:
        try:
            await env.slack_client.chat_postMessage(
                channel=channel,
                text="Wrrf, wrrf, wrrf!!!! wrrf!\n_hai! i'm watching your shipments for you now :3_",
            )
        except Exception as e:
            logging.error(f"Failed to send message to {channel} ({user_id}\n{e}")
            await env.slack_client.chat_postMessage(
                channel=user_id,
                text=f"haiii :3\nlooks like i can't send to new channel <#{channel}>, please make sure i'm in the channel uwu",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"haiii :3\nlooks like i can't send to <#{channel}>, please make sure you added me to the channel uwu :3",
                        },
                    }
                ],
            )

    for channel in removed_channels:
        try:
            await env.slack_client.chat_postMessage(
                channel=channel,
                text=":neodog_sob: i'm not watching your shipments anymore :c\n_wrrf, wrrrrrrf (sad barking noises)_",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": ":neodog_sob: i'm not watching your shipments anymore :c",
                        },
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "_wrrf, wrrrrrrf (sad barking noises)_",
                            }
                        ],
                    },
                ],
            )
        except Exception as e:
            logging.error(
                f"Failed to send message to removed channel {channel} ({user_id}\n{e}"
            )

    await env.db.user.update(
        where={"id": user_id}, data={"subscribedChannels": {"set": selected_channels}}
    )


@app.view("settings_callback")
async def settings_callback(ack: AsyncAck, body, client: AsyncWebClient):
    logging.info("URL Callback")
    user_id = body["user"]["id"]
    view = body["view"]
    actions = view["state"]["values"]
    url = actions["viewerUrl"]["url_input"]["value"]
    pattern = r"^https:\/\/shipment-viewer\.hackclub\.com\/dyn\/shipments\/[^@]+@[^?]+\?signature=[a-zA-Z0-9]+$"

    if not re.match(pattern, url):
        logging.info("DID NOT MATCH")
        return await ack(
            {"response_action": "errors", "errors": {"viewerUrl": "Invalid URL"}}
        )

    await ack()
    await env.db.user.update(
        where={"id": user_id},
        data={"viewerUrl": url, "apiUrl": url.replace("shipments", "jason")},
    )

    return await client.views_publish(
        user_id=user_id, view=await generate_home(user_id)
    )


@app.action("link")
async def link_callback(ack: AsyncAck, body, client: AsyncWebClient):
    await ack()
