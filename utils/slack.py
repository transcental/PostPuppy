import logging
import re

from slack_bolt.async_app import AsyncAck
from slack_bolt.async_app import AsyncApp

from utils.env import env
from views.home import generate_home
from views.settings import generate_settings

app = AsyncApp(token=env.slack_bot_token, signing_secret=env.slack_signing_secret)


@app.event("app_home_opened")
async def update_home_tab(client, event, logger):
    user_id = event["user"]
    view = await generate_home(user_id)
    await client.views_publish(user_id=user_id, view=view)


@app.action("open_settings")
async def open_settings(ack: AsyncAck, body, client):
    await ack()
    user_id = body["user"]["id"]
    view = await generate_settings(user_id)
    await client.views_open(trigger_id=body["trigger_id"], view=view)


@app.action("channels_select")
async def channels_callback(ack: AsyncAck, body, client):
    await ack()
    user_id = body["user"]["id"]
    view = body["view"]
    actions = view["state"]["values"]
    selected_channels = actions["channels"]["channels"]["selected_conversations"]

    await env.db.user.update(
        where={"id": user_id}, data={"subscribedChannels": {"set": selected_channels}}
    )


@app.view("settings_callback")
async def settings_callback(ack: AsyncAck, body, client):
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


@app.action("link")
async def link_callback(ack: AsyncAck, body, client):
    await ack()
